import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from urllib.parse import urlparse
import joblib
import os

# Features to extract from URL
def extract_features(url):
    features = {}
    parsed_url = urlparse(url)
    
    # 1. Length of URL
    features['url_length'] = len(url)
    
    # 2. Number of dots in URL
    features['num_dots'] = url.count('.')
    
    # 3. Presence of '@' (often used in phishing)
    features['has_at_symbol'] = 1 if '@' in url else 0
    
    # 4. Number of slashes
    features['num_slashes'] = url.count('/')
    
    # 5. Presence of IP address instead of domain
    domain = parsed_url.netloc
    features['is_ip'] = 1 if any(char.isdigit() for char in domain.split('.')) and all(part.isdigit() for part in domain.split('.') if part) else 0
    
    # 6. Length of domain
    features['domain_length'] = len(domain)
    
    return features

def generate_mock_data():
    # Synthetic data for demonstration
    data = [
        ("https://google.com", 0),
        ("https://facebook.com", 0),
        ("https://github.com", 0),
        ("http://secure-login-update.com", 1),
        ("http://192.168.1.1/login.php", 1),
        ("https://amazon.co.uk/orders", 0),
        ("http://free-gift-card-win.tk", 1),
        ("https://paypal-security-check.info", 1),
        ("https://microsoft.com", 0),
        ("http://login.verification-service.xyz", 1)
    ]
    
    df_rows = []
    for url, label in data:
        features = extract_features(url)
        features['label'] = label
        df_rows.append(features)
        
    return pd.DataFrame(df_rows)

MODEL_PATH = 'url_trust_model.pkl'

def train_model():
    print("Generating training data...")
    df = generate_mock_data()
    
    X = df.drop('label', axis=1)
    y = df['label']
    
    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    return model

def predict_url(url):
    if not os.path.exists(MODEL_PATH):
        train_model()
        
    model = joblib.load(MODEL_PATH)
    features = extract_features(url)
    features_df = pd.DataFrame([features])
    
    # Ensure column order matches training
    prediction = model.predict(features_df)[0]
    probability = model.predict_proba(features_df)[0]
    
    # label 0 = benign, 1 = malicious
    # Return a score from 0-100 (where 100 is most trustworthy)
    trust_score = int((1 - probability[1]) * 100)
    
    return {
        "prediction": "benign" if prediction == 0 else "malicious",
        "trust_score": trust_score,
        "probability_malicious": probability[1]
    }

if __name__ == "__main__":
    train_model()
    test_url = "https://google.com"
    print(f"Prediction for {test_url}: {predict_url(test_url)}")
    test_url_mal = "http://phish-site.tk/login"
    print(f"Prediction for {test_url_mal}: {predict_url(test_url_mal)}")
