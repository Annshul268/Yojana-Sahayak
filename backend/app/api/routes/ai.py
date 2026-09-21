"""AI Endpoints for Grounded Explanations and Conversational Q&A."""

from fastapi import APIRouter
from backend.app.ai.service import ai_service
from backend.app.schemas.ai import (
    AskAIRequest,
    AskAIResponse,
    ExplainEligibilityRequest,
    ExplainEligibilityResponse,
)

router = APIRouter(prefix="/ai", tags=["AI Scheme Assistant"])


@router.post("/explain", response_model=ExplainEligibilityResponse, summary="Grounded Scheme Eligibility Explanation")
async def explain_eligibility(payload: ExplainEligibilityRequest) -> ExplainEligibilityResponse:
    explanation = await ai_service.explain_eligibility(
        match_result=payload.match_result,
        user_profile_dict=payload.user_profile,
        language=payload.language,
    )
    return ExplainEligibilityResponse(
        scheme_id=payload.match_result.scheme_id,
        scheme_name=payload.match_result.scheme_name,
        explanation=explanation,
        language=payload.language,
    )


@router.post("/ask", response_model=AskAIResponse, summary="Ask Scheme Questions Grounded in Government Data")
async def ask_ai(payload: AskAIRequest) -> AskAIResponse:
    result = await ai_service.answer_question(
        question=payload.question,
        language=payload.language,
        category=payload.category,
    )
    return AskAIResponse(**result)
