import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("Testing /health...")
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Failed: {e}")

def test_validate_mock():
    print("\nTesting /api/v1/validate (Expect Mock Fallback)...")
    payload = {
        "phone_number": "14155552671",
        "country_code": "US",
        "context": {"user_id": "test_1"}
    }
    try:
        r = requests.post(f"{BASE_URL}/api/v1/validate", json=payload)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Success: {data['success']}")
            print(f"Strategy: {data['validation_strategy']}")
            print(f"Confidence: {data['confidence_score']}")
            print(f"Provider Used: {data['retry_metadata'].get('provider')}")
            print(f"Trace: {json.dumps(data['decision_trace'], indent=2)}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    # Wait for server to potentially start
    time.sleep(2)
    test_health()
    test_validate_mock()
