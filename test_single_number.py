import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_single_number(phone, context="test"):
    """Test a single phone number"""
    print(f"\n🔍 Testing: {phone}")
    print("=" * 60)
    
    payload = {
        "phone_number": phone,
        "context": {
            "user_id": "test123",
            "source": context
        }
    }
    
    try:
        r = requests.post(f"{BASE_URL}/api/v1/validate", json=payload)
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Status: SUCCESS")
            print(f"📱 Formatted: {data.get('formatted_number', 'N/A')}")
            print(f"🌍 Country: {data.get('country_code', 'N/A')}")
            print(f"📞 Carrier: {data.get('carrier_name', 'N/A')}")
            print(f"💬 WhatsApp: {data.get('whatsapp_available', 'N/A')}")
            print(f"🎯 Confidence: {data.get('confidence_score', 'N/A')}")
            print(f"💭 Reasoning: {data.get('reasoning', 'N/A')[:150]}")
            print(f"\n📊 Full Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    # Test the user's number
    test_single_number("+917094801807", "user_number")
    
    # Test with country code explicitly
    test_single_number("917094801807", "without_plus")
    
    # Test another Indian number
    test_single_number("+919876543210", "another_indian")
