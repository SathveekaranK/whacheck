import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_with_country():
    """Test single validation WITH country code"""
    print("🔍 Testing +917094801807 with country code IN\n" + "="*60)
    
    payload = {
        "phone_number": "+917094801807",
        "country_code": "IN",  # IMPORTANT: Include this!
        "context": {
            "user_id": "test_user",
            "source": "test"
        }
    }
    
    try:
        r = requests.post(f"{BASE_URL}/api/v1/validate", json=payload)
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ SUCCESS!\n")
            print(f"📱 Formatted: {data.get('formatted_number')}")
            print(f"🌍 Country: {data.get('country_code')}")
            print(f"📞 Carrier: {data.get('carrier')}")
            print(f"📋 Line Type: {data.get('line_type')}")
            print(f"💬 WhatsApp: {data.get('whatsapp_available')}")
            print(f"🎯 Confidence: {data.get('confidence_score')}")
            print(f"💭 Reasoning: {data.get('reasoning')}")
            print(f"⚡ Strategy: {data.get('validation_strategy')}")
        else:
            print(f"❌ Error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_with_country()
