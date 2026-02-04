from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.api.models import ValidateRequest, ValidateResponse, ConfidenceBreakdown
from app.core.database import get_db
from app.agents.decision import decision_agent
from app.agents.retry import retry_agent
from app.agents.confidence import confidence_agent
from app.agents.learning import learning_agent
from app.agents.types import ValidationStrategy
from app.db.models import ValidationHistory
from app.core.csv_processor import process_csv_batch
from typing import Dict, Any

router = APIRouter()

@router.post("/validate/batch")
async def batch_validate(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload CSV -> Process -> Return CSV
    """
    content = await file.read()
    processed_csv = await process_csv_batch(content, db)
    
    return Response(
        content=processed_csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=validated_results.csv"}
    )


@router.post("/validate", response_model=ValidateResponse)
async def validate_phone_number(
    request: ValidateRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # 1. Check History
    history = db.query(ValidationHistory).filter(ValidationHistory.phone_number == request.phone_number).first()
    
    # 2. Pre-check / NumVerify (Agent 2 Helper) called early for Decision signals
    numverify_result = await retry_agent.validate_format(request.phone_number, request.country_code)
    
    # 3. Decision Agent
    trace = decision_agent.decide(
        request.phone_number,
        request.country_code,
        history,
        numverify_result
    )
    
    whatsapp_result = {"available": False, "provider": "skipped"}
    retry_meta = {}
    
    # 4. Execution Logic
    if trace.final_decision == ValidationStrategy.IMMEDIATE:
        # Run Validation
        whatsapp_result = await retry_agent.check_whatsapp_availability(request.phone_number)
        retry_meta = whatsapp_result
        
        # Update Background Stats (Learning - Provider Health)
        if whatsapp_result["provider"] != "mock": # Don't skew stats with mock
             background_tasks.add_task(
                 learning_agent.update_provider_metrics,
                 db, 
                 whatsapp_result["provider"],
                 whatsapp_result["available"],
                 1.0 # Placeholder response time, can improve later
             )

    elif trace.final_decision == ValidationStrategy.SKIP and history:
        # Use Cached Data
        whatsapp_result = {
            "available": history.whatsapp_available, 
            "provider": "cache"
        }
    
    # 5. Confidence Scoring
    confidence = confidence_agent.calculate_score(
        is_valid_format=numverify_result.get("valid", False),
        whatsapp_exists=whatsapp_result.get("available", False),
        provider_used=whatsapp_result.get("provider", "none"),
        history_present=bool(history)
    )
    
    # 6. Learning (Record Decision)
    background_tasks.add_task(learning_agent.record_decision, db, request.phone_number, trace.final_decision, trace)
    
    # 7. Update History (if new or changed)
    # (Simplified: Just update timestamp or create new)
    # In real app, upsert logic.
    
    return ValidateResponse(
        success=True,
        phone_number=request.phone_number,
        formatted_number=numverify_result.get("international_format", request.phone_number),
        country_code=request.country_code,
        carrier=numverify_result.get("carrier"),
        line_type=numverify_result.get("line_type"),
        whatsapp_available=whatsapp_result.get("available", False),
        validation_strategy=trace.final_decision,
        confidence_score=confidence["score"],
        confidence_breakdown=ConfidenceBreakdown(
            score=confidence["score"],
            classification=confidence["classification"],
            signals=confidence["breakdown"],
            recommendation=confidence["classification"]
        ),
        decision_trace=trace,
        retry_metadata=retry_meta,
        reasoning=trace.reasoning
    )

@router.get("/analytics/insights")
def get_insights(db: Session = Depends(get_db)):
    # Simple placeholder for analytics
    return {"status": "Analytics module ready"}
