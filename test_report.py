import requests
import os

def test_report_flow():
    url = "http://127.0.0.1:5000"
    data = {
        "url": "google.com",
        "trustScore": 95,
        "riskScore": 5,
        "verdict": "SAFE",
        "message": "Institutional authority verified."
    }
    
    print("Testing report generation...")
    try:
        response = requests.post(f"{url}/api/generate_report", json=data)
        if response.status_code == 200:
            res_data = response.json()
            filename = res_data.get('filename')
            print(f"Success! Filename: {filename}")
            
            print("Testing report download...")
            download_res = requests.get(f"{url}/api/download/{filename}")
            if download_res.status_code == 200:
                print(f"Download successful! Size: {len(download_res.content)} bytes")
            else:
                print(f"Download failed: {download_res.status_code}")
        else:
            print(f"Generation failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_report_flow()
