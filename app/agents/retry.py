import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logger import logger
from app.agents.types import ValidationResult, ValidationStrategy

class RetryAgent:
    """
    Agent 2: Handles external API calls with retries and failover.
    """
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=10)

    async def validate_format(self, phone_number: str, country_code: str) -> Dict[str, Any]:
        """
        Validates format using NumVerify (or local fallback).
        """
        if not settings.NUMVERIFY_API_KEY:
             logger.warning("NumVerify API Key missing, skipping enhanced format check.")
             return {"valid": True, "line_type": "unknown (api_key_missing)"}

        url = f"http://apilayer.net/api/validate?access_key={settings.NUMVERIFY_API_KEY}&number={phone_number}&country_code={country_code}&format=1"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"NumVerify response for {phone_number}: {data}")
                        return data
                    else:
                        logger.error(f"NumVerify failed: {response.status}")
                        return {"valid": False, "line_type": "unknown (error)", "carrier": "unknown (error)"}
        except Exception as e:
            logger.error(f"NumVerify exception for {phone_number}: {str(e)}")
            return {"valid": False, "line_type": "unknown (exception)", "carrier": "unknown (exception)"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, TimeoutError))
    )
    async def _call_whapi(self, phone_number: str) -> bool:
        """Primary Provider: Whapi.cloud"""
        if not settings.WHAPI_API_TOKEN:
            raise ValueError("Whapi Token missing")
            
        # Example Endpoint - Adjust strictly to Whapi API docs
        url = "https://gate.whapi.cloud/contacts"
        headers = {
            "Authorization": f"Bearer {settings.WHAPI_API_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "blocking": "wait",
            "contacts": [phone_number]
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # Parse Whapi response to check if 'status' is 'valid'
                    contacts = data.get("contacts", [])
                    if contacts:
                        return contacts[0].get("status") == "valid"
                    return False
                raise aiohttp.ClientError(f"Whapi Error: {response.status}")

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5)
    )
    async def _call_mock(self, phone_number: str) -> bool:
        """Fallback: Mock Provider"""
        logger.info(f"Using Mock Provider for {phone_number}")
        return True

    async def check_whatsapp_availability(self, phone_number: str) -> Dict[str, Any]:
        """
        Orchestrates the failover: Whapi -> Mock
        """
        providers_tried = []
        
        # 1. Try Whapi
        try:
            is_valid = await self._call_whapi(phone_number)
            return {"available": is_valid, "provider": "whapi", "tried": ["whapi"]}
        except Exception as e:
            logger.warning(f"Whapi failed: {e}")
            providers_tried.append("whapi")

        # 2. Fallback to Mock
        is_valid = await self._call_mock(phone_number)
        return {"available": is_valid, "provider": "mock", "tried": providers_tried + ["mock"]}

retry_agent = RetryAgent()
