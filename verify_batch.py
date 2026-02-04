import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_batch_upload():
    print("\nTesting /api/v1/validate/batch...")
    try:
        with open("test_batch.csv", "rb") as f:
            files = {"file": ("test_batch.csv", f, "text/csv")}
            r = requests.post(f"{BASE_URL}/api/v1/validate/batch", files=files)
            
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            # Save result to file
            with open("batch_results.csv", "wb") as out:
                out.write(r.content)
            print("✅ Success! Results saved to: batch_results.csv")
            print("\n📊 Preview of results:")
            print(r.text[:800])  # Print preview
        else:
            print(f"❌ Error: {r.text}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    time.sleep(2)
    test_batch_upload()
