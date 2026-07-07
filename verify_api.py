import requests
import json

def test_analyze(url):
    print(f"Testing URL: {url}")
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/analyze',
            json={'url': url}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response Data:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_analyze("google.com")
    print("-" * 20)
    test_analyze("phish-site.tk/login")
