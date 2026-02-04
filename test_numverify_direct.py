import asyncio
import aiohttp

# Test NumVerify API directly
async def test_numverify():
    api_key = "110e224a0d59111e0d1c0081fd3ccab7"
    
    # Test numbers
    numbers = [
        ("+917094801807", "IN"),
        ("917094801807", "IN"),
        ("7094801807", "IN"),
    ]
    
    for phone, country in numbers:
        print(f"\n🔍 Testing: {phone} (Country: {country})")
        print("=" * 60)
        
        # NumVerify API endpoint
        url = f"http://apilayer.net/api/validate?access_key={api_key}&number={phone}&country_code={country}&format=1"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    print(f"Status Code: {response.status}")
                    data = await response.json()
                    print(f"Response: {data}")
                    
                    if data.get("valid"):
                        print(f"✅ Valid: Yes")
                        print(f"📱 Formatted: {data.get('international_format', 'N/A')}")
                        print(f"🌍 Country: {data.get('country_name', 'N/A')}")
                        print(f"📞 Carrier: {data.get('carrier', 'N/A')}")
                        print(f"📋 Line Type: {data.get('line_type', 'N/A')}")
                    else:
                        print(f"❌ Valid: No")
                        
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_numverify())
