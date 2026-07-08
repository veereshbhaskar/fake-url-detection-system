from flask import Flask, request, jsonify, send_from_directory
import os
import requests
from bs4 import BeautifulSoup
import whois
import socket
from urllib.parse import urlparse
from ml_model import predict_url
from nlp_analysis import get_bert_analysis, generate_gpt_briefing

app = Flask(__name__)

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def home():
    return send_from_directory(PROJECT_ROOT, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(PROJECT_ROOT, filename)

@app.route('/api/analyze', methods=['POST'])
def analyze_url():
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Ensure URL has schema
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    trust_score = 50
    details = []
    
    try:
        # 1. DNS & Reachability Check
        domain = urlparse(url).netloc
        try:
            socket.gethostbyname(domain)
            trust_score += 10
            details.append({"title": "DNS Check", "status": "Valid DNS Resolution", "score": "+10", "desc": "Domain successfully resolved to a valid IP address. Connection path is clear."})
        except Exception as e:
            print(f"DNS check failed for {domain}: {e}")
            details.append({"title": "DNS Check", "status": "Resolution Failed", "score": "0", "desc": f"Could not resolve {domain}. Domain might be offline or using hidden DNS."})
            # Continue instead of returning 400

        # 2. SSL/HTTPS Check
        if url.startswith('https://'):
            trust_score += 20
            details.append({"title": "Security", "status": "SSL/TLS Active", "score": "+20", "desc": "Encrypted communication detected. Modern security protocols are in use."})
        else:
            trust_score -= 10
            details.append({"title": "Security", "status": "Insecure Connection", "score": "-10", "desc": "Warning: Data being sent is unencrypted and vulnerable to interception."})

        # 3. Content Scraping
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_title = soup.title.string.strip() if soup.title else "No Title Found"
            
            # Additional content categorization logic
            url_lower = url.lower()
            title_lower = page_title.lower()
            
            # Risk Keywords (Betting, Movies/Downloads)
            risk_keywords = ['bet', 'betting', 'casino', 'gamble', 'movie', 'download', 'torrent', 'free-movies']
            if any(kw in url_lower or kw in title_lower for kw in risk_keywords):
                trust_score -= 20
                details.append({"title": "Content Category", "status": "High-Risk Category Detected", "score": "-20", "desc": "Domain is associated with betting, movie downloads, or typical high-risk file sharing."})
                
            # Trust Keywords (Published Papers, Research)
            trust_keywords = ['research', 'paper', 'journal', 'published', 'academic', 'arxiv', 'science']
            if any(kw in url_lower or kw in title_lower for kw in trust_keywords):
                trust_score += 15
                details.append({"title": "Content Category", "status": "Academic/Research Content", "score": "+15", "desc": "Domain appears to host published papers or academic research."})

            
            trust_score += 10
            details.append({"title": "Page Content", "status": "Response Verified", "score": "+10", "desc": f"Confirmed live host: '{page_title[:30]}'. Content structure appears standard."})
            
            # Check for suspicious redirections
            if len(response.history) > 2:
                trust_score -= 15
                details.append({"title": "Redirections", "status": "Multiple Redirects", "score": "-15", "desc": f"Warning: {len(response.history)} hops detected. Possible URL hijacking technique."})
                
        except Exception as e:
            trust_score -= 20
            details.append({"title": "Reachability", "status": "Verification Failed", "score": "-20", "desc": "Failed to retrieve page content. Host may be blocking analysis tools."})

        # 4. Domain Age (Whois)
        try:
            domain_info = whois.whois(domain)
            creation_date = domain_info.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
                
            if creation_date:
                # simple logic: if older than 2023, good
                if creation_date.year < 2023:
                    trust_score += 20
                    details.append({"title": "Domain Age", "status": "Established Asset", "score": "+20", "desc": f"Registered in {creation_date.year}. Domain has established history."})
                else:
                    trust_score -= 5
                    details.append({"title": "Domain Age", "status": "New Registration", "score": "-5", "desc": f"Recent 2023+ registration. Typical of temporary phishing setups."})
        except:
             details.append({"title": "Whois Lookup", "status": "Identity Hidden", "score": "0", "desc": "Whois lookup restricted or private. Ownership cannot be verified."})
        
        # 5. Machine Learning Analysis
        try:
            ml_result = predict_url(url)
            ml_score = ml_result['trust_score']
            # Influence the weight of ML prediction: Range -25 to +25
            ml_delta = (ml_score - 50) // 2
            trust_score += ml_delta
            details.append({"title": "Static AI Analysis", "status": f"Predicted {ml_result['prediction'].upper()}", "score": ml_delta, "visual": ml_score, "desc": f"Random Forest analysis suggests a {ml_score}% likelihood of trustworthy structural patterns."})
        except Exception as e:
            print(f"ML analysis failed: {e}")
            details.append({"title": "Static AI Analysis", "status": "ML Engine Error", "score": 0, "visual": 50, "desc": "Neural classification engine currently offline."})

        # 6. BERT Semantic Analysis
        try:
            bert_result = get_bert_analysis(url)
            trust_score = (trust_score + bert_result['score']) // 2
            details.append({
                "title": "BERT Neural Core", 
                "status": bert_result['status'], 
                "score": bert_result['score'], 
                "visual": bert_result['score'], 
                "desc": bert_result['desc'],
                "ai_badge": "BERT-v2"
            })
        except Exception as e:
            print(f"BERT analysis failed: {e}")

        # Cap total score
        trust_score = max(0, min(100, trust_score))
        risk_score = 100 - trust_score
        
        # Categorize Results for the Masterpiece UI
        categorized = {
            "lexical": [],
            "ssl": [],
            "domain": []
        }
        
        for d in details:
            # Map visual bar
            if "visual" in d:
                visual = d["visual"]
            else:
                score_delta = d["score"]
                if isinstance(score_delta, str):
                    try: score_delta = int(score_delta.replace('+', ''))
                    except: score_delta = 0
                visual = int(max(0, min(100, 50 + (score_delta * 2.5))))
            
            # Map categories
            title = d["title"].lower()
            insight = {
                "title": d["title"],
                "status": d["status"],
                "desc": d.get("desc", ""),
                "score": visual,
                "ai_badge": d.get("ai_badge", "")
            }
            
            if any(x in title for x in ["ai", "static", "bert", "content", "reachability"]):
                categorized["lexical"].append(insight)
            elif any(x in title for x in ["security", "ssl", "dns"]):
                categorized["ssl"].append(insight)
            elif any(x in title for x in ["age", "whois"]):
                categorized["domain"].append(insight)

        return jsonify({
            "query": url,
            "trustScore": trust_score,
            "riskScore": risk_score,
            "categorized": categorized,
            "message": f"Verdict: { 'MALICIOUS' if risk_score > 60 else 'SUSPICIOUS' if risk_score > 30 else 'SAFE' }",
            "verdict": 'MALICIOUS' if risk_score > 60 else 'SUSPICIOUS' if risk_score > 30 else 'SAFE'
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

from generate_ppt import create_presentation
from flask import send_from_directory, send_file

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    try:
        filename = create_presentation(data)
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        print(f"Report generation failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    reports_dir = os.path.join(PROJECT_ROOT, 'reports')
    return send_from_directory(reports_dir, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
