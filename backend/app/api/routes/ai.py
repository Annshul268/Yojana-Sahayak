"""AI Endpoints for Grounded Explanations and Conversational Q&A."""

from fastapi import APIRouter, HTTPException
from backend.app.ai.service import ai_service
from backend.app.core.logging import logger
from backend.app.schemas.ai import (
    AskAIRequest,
    AskAIResponse,
    ExplainEligibilityRequest,
    ExplainEligibilityResponse,
)

router = APIRouter(prefix="/ai", tags=["AI Scheme Assistant"])


@router.post("/explain", response_model=ExplainEligibilityResponse, summary="Grounded Scheme Eligibility Explanation")
async def explain_eligibility(payload: ExplainEligibilityRequest) -> ExplainEligibilityResponse:
    try:
        explanation = await ai_service.explain_eligibility(
            match_result=payload.match_result,
            user_profile_dict=payload.user_profile,
            language=payload.language,
            scheme_id=payload.scheme_id,
            scheme_slug=payload.scheme_slug,
        )
        s_id = payload.scheme_id or (payload.match_result.scheme_id if payload.match_result else (payload.scheme_slug or "scheme"))
        s_name = (payload.match_result.scheme_name if payload.match_result else (payload.scheme_slug or "Government Scheme"))
        return ExplainEligibilityResponse(
            scheme_id=s_id,
            scheme_name=s_name,
            explanation=explanation,
            language=payload.language,
        )
    except Exception as exc:
        logger.error("AI explain endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail="AI explanation service is temporarily unavailable.")


@router.post("/ask", response_model=AskAIResponse, summary="Ask Scheme Questions Grounded in Government Data")
async def ask_ai(payload: AskAIRequest) -> AskAIResponse:
    try:
        result = await ai_service.answer_question(
            question=payload.question,
            language=payload.language,
            category=payload.category,
            scheme_id=payload.scheme_id,
            scheme_slug=payload.scheme_slug,
        )
        return AskAIResponse(**result)
    except Exception as exc:
        logger.error("AI ask endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail="AI assistant service is temporarily unavailable.")
