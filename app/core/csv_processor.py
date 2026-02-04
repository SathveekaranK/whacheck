import pandas as pd
import io
from typing import List, Dict, Any
from app.api.models import ValidateRequest
from app.agents.decision import decision_agent
from app.agents.retry import retry_agent
from app.agents.confidence import confidence_agent
from app.agents.types import ValidationStrategy
from app.db.models import ValidationHistory
from app.core.logger import logger
from sqlalchemy.orm import Session
import asyncio

async def process_csv_batch(content: bytes, db: Session) -> bytes:
    """
    Process a CSV file: 
    1. Parse phone numbers
    2. Run validation for each
    3. Return CSV with results
    """
    # Load CSV
    df = pd.read_csv(io.BytesIO(content))
    
    # Identify Phone Number Column (Naive approach: look for 'phone', 'mobile', 'call' or 1st col)
    phone_col = None
    for col in df.columns:
        if "phone" in col.lower() or "mobile" in col.lower() or "number" in col.lower():
            phone_col = col
            break
    if not phone_col:
        phone_col = df.columns[0]
        
    results = []
    
    # Process each row (limited concurrency for prototype)
    # In a real app, this would be a proper Task Queue (Celery/RQ)
    for _, row in df.iterrows():
        phone = str(row[phone_col])
        
        # Extract country code from CSV if available, otherwise default to US
        country = "US"
        if "country_code" in df.columns:
            country = str(row["country_code"])
        elif "country" in df.columns:
            country = str(row["country"])
        
        
        # 1. History
        history = db.query(ValidationHistory).filter(ValidationHistory.phone_number == phone).first()
        
        # 2. Pre-check
        numverify_result = await retry_agent.validate_format(phone, country)
        
        # 3. Decision
        trace = decision_agent.decide(phone, country, history, numverify_result)
        
        # 4. Action
        whatsapp_result = {"available": False}
        if trace.final_decision == ValidationStrategy.IMMEDIATE:
            whatsapp_result = await retry_agent.check_whatsapp_availability(phone)
        elif trace.final_decision == ValidationStrategy.SKIP and history:
            whatsapp_result = {"available": history.whatsapp_available}
            
        # 5. Score
        confidence = confidence_agent.calculate_score(
            numverify_result.get("valid", False),
            whatsapp_result.get("available", False),
            whatsapp_result.get("provider", "none"),
            bool(history)
        )
        
        # Collect Result
        results.append({
            "Original_Phone": f"'{phone}",  # Prefix with ' to prevent Excel scientific notation
            "Formatted_Number": numverify_result.get("international_format", numverify_result.get("number", phone)),
            "Line_Type": numverify_result.get("line_type", "unknown"),
            "Carrier": numverify_result.get("carrier", "unknown"),
            "Country": numverify_result.get("country_name", country),
            "WhatsApp_Available": whatsapp_result.get("available", False),
            "Confidence_Score": confidence["score"],
            "Validation_Trace": trace.reasoning[:100] + "..." if len(trace.reasoning) > 100 else trace.reasoning
        })
        
    # Create Result DataFrame
    result_df = pd.DataFrame(results)
    
    # Merge back with original (optional, or just return result_df)
    # let's just return the result_df for clarity + original phone matches
    
    output = io.BytesIO()
    result_df.to_csv(output, index=False)
    return output.getvalue()
