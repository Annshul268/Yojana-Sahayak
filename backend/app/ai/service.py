"""AI service coordinating grounded scheme explanations and Q&A."""

from typing import Any, Dict, Optional
from backend.app.ai.groq_provider import groq_provider
from backend.app.ai.prompts import ELIGIBILITY_EXPLANATION_PROMPT, SYSTEM_GROUNDING_PROMPT
from backend.app.matching.models import SchemeMatchResult
from backend.app.rag.retriever import scheme_retriever


class AIService:
    """Provides grounded AI interactions backed by ChromaDB retrieval and Groq."""

    def __init__(self, provider=groq_provider, retriever=scheme_retriever):
        self.provider = provider
        self.retriever = retriever

    async def explain_eligibility(
        self,
        match_result: SchemeMatchResult,
        user_profile_dict: Dict[str, Any],
        language: str = "en",
    ) -> str:
        """Generates a grounded citizen-friendly explanation of why a scheme matched."""
        if not self.provider.is_available():
            # Grounded rule summary fallback
            lang_hi = language.lower() == "hi"
            lines = []
            if lang_hi:
                lines.append(f"### {match_result.scheme_name} के लिए आपकी पात्रता स्थिति: **{match_result.status.value.replace('_', ' ').title()}** (स्कोर: {match_result.score}/100)")
                if match_result.matched_rules:
                    lines.append("\n**सत्यापित शर्तें:**")
                    for r in match_result.matched_rules:
                        lines.append(f"- {r.rule_name}: {r.reason}")
                if match_result.failed_rules:
                    lines.append("\n**अपात्रता के कारण:**")
                    for r in match_result.failed_rules:
                        lines.append(f"- {r.rule_name}: {r.reason}")
                if match_result.missing_information:
                    lines.append("\n**अतिरिक्त दस्तावेज़ / आवश्यक जानकारी:**")
                    for m in match_result.missing_information:
                        lines.append(f"- {m.get('field')}: {m.get('reason')}")
                lines.append(f"\nआधिकारिक पोर्टल: [{match_result.official_url}]({match_result.official_url})")
            else:
                lines.append(f"### Your Eligibility Status for {match_result.scheme_name}: **{match_result.status.value.replace('_', ' ').title()}** (Match Score: {match_result.score}/100)")
                if match_result.matched_rules:
                    lines.append("\n**Satisfied Criteria:**")
                    for r in match_result.matched_rules:
                        lines.append(f"- {r.rule_name.replace('_', ' ').title()}: {r.reason}")
                if match_result.failed_rules:
                    lines.append("\n**Unmet Criteria:**")
                    for r in match_result.failed_rules:
                        lines.append(f"- {r.rule_name.replace('_', ' ').title()}: {r.reason}")
                if match_result.missing_information:
                    lines.append("\n**Pending Verification / Missing Details:**")
                    for m in match_result.missing_information:
                        lines.append(f"- {m.get('field', '').replace('_', ' ').title()}: {m.get('reason')}")
                lines.append(f"\nOfficial Portal: [{match_result.official_url}]({match_result.official_url})")
            return "\n".join(lines)

        prompt = ELIGIBILITY_EXPLANATION_PROMPT.format(
            status=match_result.status.value,
            scheme_name=match_result.scheme_name,
            user_profile=str(user_profile_dict),
            scheme_rules=f"Matched: {[r.model_dump() for r in match_result.matched_rules]}; Failed: {[r.model_dump() for r in match_result.failed_rules]}",
            benefits="; ".join(match_result.benefits),
            official_url=match_result.official_url,
            language="Hindi" if language.lower() == "hi" else "English",
        )

        messages = [
            {"role": "system", "content": SYSTEM_GROUNDING_PROMPT.format(context=f"Scheme: {match_result.scheme_name}\nOfficial URL: {match_result.official_url}")},
            {"role": "user", "content": prompt},
        ]
        return await self.provider.generate_response(messages)

    async def answer_question(
        self,
        question: str,
        language: str = "en",
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Answers a user question grounded in retrieved scheme documents."""
        # 1. Retrieve top relevant context documents from ChromaDB
        relevant_docs = self.retriever.retrieve_relevant_schemes(
            query=question,
            top_k=3,
            category=category,
        )

        if not relevant_docs:
            context_str = "No specific government schemes found matching this query in the verified database."
        else:
            context_str = "\n\n---\n\n".join([doc["document"] for doc in relevant_docs])

        # 2. Call provider with grounding prompt
        system_prompt = SYSTEM_GROUNDING_PROMPT.format(context=context_str)
        user_prompt = f"Citizen Question: {question}\nLanguage: {'Hindi' if language.lower() == 'hi' else 'English'}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        answer = await self.provider.generate_response(messages)

        # 3. Extract references
        references = [
            {
                "scheme_id": doc["scheme_id"],
                "category": doc["metadata"].get("category", ""),
                "official_url": doc["metadata"].get("official_url", ""),
            }
            for doc in relevant_docs
        ]

        return {
            "question": question,
            "answer": answer,
            "language": language,
            "grounded_references": references,
        }


ai_service = AIService()
