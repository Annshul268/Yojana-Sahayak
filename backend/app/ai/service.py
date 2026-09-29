"""AI service coordinating grounded scheme explanations and Q&A."""

from typing import Any, Dict, List, Optional
from backend.app.ai.groq_provider import groq_provider
from backend.app.ai.prompts import (
    ELIGIBILITY_EXPLANATION_PROMPT,
    SCHEME_EXPLANATION_PROMPT,
    SYSTEM_GROUNDING_PROMPT,
)
from backend.app.core.logging import logger
from backend.app.matching.models import SchemeMatchResult
from backend.app.rag.retriever import scheme_retriever


class AIService:
    """Provides grounded AI interactions backed by ChromaDB retrieval, database lookup, and Groq."""

    def __init__(self, provider=groq_provider, retriever=scheme_retriever):
        self.provider = provider
        self.retriever = retriever

    async def _lookup_scheme(self, identifier: Optional[str]) -> Optional[Dict[str, Any]]:
        """Queries the verified scheme database by slug or UUID."""
        if not identifier:
            return None
        try:
            from sqlalchemy import or_, select
            from backend.app.database.connection import AsyncSessionLocal
            from backend.app.database.models import Scheme

            async with AsyncSessionLocal() as session:
                stmt = select(Scheme).where(or_(Scheme.slug == identifier, Scheme.id == identifier))
                result = await session.execute(stmt)
                scheme = result.scalar_one_or_none()
                if scheme:
                    return {
                        "id": scheme.id,
                        "slug": scheme.slug,
                        "name": scheme.name,
                        "name_hi": scheme.name_hi,
                        "description": scheme.description,
                        "description_hi": scheme.description_hi,
                        "category": scheme.category,
                        "ministry": scheme.ministry,
                        "level": scheme.level,
                        "benefits": scheme.benefits or [],
                        "documents": scheme.documents or [],
                        "eligibility_rules": scheme.eligibility_rules or {},
                        "application_steps": scheme.application_steps or [],
                        "official_url": scheme.official_url,
                    }
        except Exception as exc:
            logger.warning("Database lookup for scheme '%s' failed: %s", identifier, exc)
        return None

    async def explain_eligibility(
        self,
        match_result: Optional[SchemeMatchResult] = None,
        user_profile_dict: Optional[Dict[str, Any]] = None,
        language: str = "en",
        scheme_id: Optional[str] = None,
        scheme_slug: Optional[str] = None,
    ) -> str:
        """Generates a grounded citizen-friendly explanation of why a scheme matched or scheme details."""
        lang_hi = language.lower() == "hi"

        # Case 1: Full match result provided
        if match_result:
            if not self.provider.is_available():
                # Grounded rule summary fallback
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
                user_profile=str(user_profile_dict or {}),
                scheme_rules=f"Matched: {[r.model_dump() for r in match_result.matched_rules]}; Failed: {[r.model_dump() for r in match_result.failed_rules]}",
                benefits="; ".join(match_result.benefits),
                official_url=match_result.official_url,
                language="Hindi" if lang_hi else "English",
            )
            messages = [
                {"role": "system", "content": SYSTEM_GROUNDING_PROMPT.format(context=f"Scheme: {match_result.scheme_name}\nOfficial URL: {match_result.official_url}")},
                {"role": "user", "content": prompt},
            ]
            return await self.provider.generate_response(messages)

        # Case 2: Direct scheme ID/slug lookup
        target_id = scheme_slug or scheme_id
        scheme = await self._lookup_scheme(target_id)
        if not scheme:
            if lang_hi:
                return "इस योजना का विवरण सत्यापित डेटाबेस में नहीं मिला।"
            return "Details for this scheme could not be found in the verified database."

        s_name = scheme.get("name_hi") if lang_hi and scheme.get("name_hi") else scheme.get("name")
        s_desc = scheme.get("description_hi") if lang_hi and scheme.get("description_hi") else scheme.get("description")
        benefits_list = scheme.get("benefits", [])
        docs_list = scheme.get("documents", [])
        official_url = scheme.get("official_url", "")

        # Fallback when Groq provider is not configured or unavailable
        if not self.provider.is_available():
            if lang_hi:
                lines = [
                    f"### {s_name} - आधिकारिक विवरण",
                    f"{s_desc}\n",
                ]
                if benefits_list:
                    lines.append("**मुख्य लाभ:**")
                    lines.extend([f"- {b}" for b in benefits_list])
                    lines.append("")
                if docs_list:
                    lines.append("**आवश्यक दस्तावेज़:**")
                    lines.extend([f"- {d}" for d in docs_list])
                    lines.append("")
                lines.append(f"**आधिकारिक पोर्टल:** [{official_url}]({official_url})")
            else:
                lines = [
                    f"### {s_name} - Verified Scheme Overview",
                    f"{s_desc}\n",
                ]
                if benefits_list:
                    lines.append("**Key Benefits:**")
                    lines.extend([f"- {b}" for b in benefits_list])
                    lines.append("")
                if docs_list:
                    lines.append("**Required Documents:**")
                    lines.extend([f"- {d}" for d in docs_list])
                    lines.append("")
                lines.append(f"**Official Portal:** [{official_url}]({official_url})")
            return "\n".join(lines)

        # LLM generation using verified scheme data
        scheme_context = (
            f"Scheme Name: {s_name}\n"
            f"Category: {scheme.get('category')}\n"
            f"Ministry: {scheme.get('ministry')}\n"
            f"Description: {s_desc}\n"
            f"Benefits: {'; '.join(str(b) for b in benefits_list)}\n"
            f"Documents: {'; '.join(str(d) for d in docs_list)}\n"
            f"Eligibility Rules: {scheme.get('eligibility_rules')}\n"
            f"Official URL: {official_url}"
        )
        prompt = SCHEME_EXPLANATION_PROMPT.format(
            scheme_name=s_name,
            scheme_details=scheme_context,
            official_url=official_url,
            language="Hindi" if lang_hi else "English",
        )
        messages = [
            {"role": "system", "content": SYSTEM_GROUNDING_PROMPT.format(context=scheme_context)},
            {"role": "user", "content": prompt},
        ]
        return await self.provider.generate_response(messages)

    async def answer_question(
        self,
        question: str,
        language: str = "en",
        category: Optional[str] = None,
        scheme_id: Optional[str] = None,
        scheme_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Answers a user question grounded in retrieved scheme documents and verified database information."""
        lang_hi = language.lower() == "hi"

        # 1. Direct database lookup if scheme identifier is provided
        target_id = scheme_slug or scheme_id
        scheme_data = await self._lookup_scheme(target_id) if target_id else None

        verified_context_parts = []
        if scheme_data:
            s_name = scheme_data.get("name_hi") if lang_hi and scheme_data.get("name_hi") else scheme_data.get("name")
            s_desc = scheme_data.get("description_hi") if lang_hi and scheme_data.get("description_hi") else scheme_data.get("description")
            benefits_str = "; ".join(str(b) for b in scheme_data.get("benefits", []))
            docs_str = "; ".join(str(d) for d in scheme_data.get("documents", []))
            verified_context_parts.append(
                f"VERIFIED DATABASE RECORD FOR THIS SCHEME:\n"
                f"- Name: {s_name}\n"
                f"- Category: {scheme_data.get('category')}\n"
                f"- Ministry: {scheme_data.get('ministry')}\n"
                f"- Description: {s_desc}\n"
                f"- Benefits: {benefits_str}\n"
                f"- Required Documents: {docs_str}\n"
                f"- Eligibility Rules: {scheme_data.get('eligibility_rules')}\n"
                f"- Official URL: {scheme_data.get('official_url')}"
            )

        # 2. Retrieve top relevant context documents from ChromaDB
        relevant_docs = []
        try:
            relevant_docs = self.retriever.retrieve_relevant_schemes(
                query=question,
                top_k=3,
                category=category or (scheme_data.get("category") if scheme_data else None),
            )
        except Exception as exc:
            logger.warning("RAG retrieval failed: %s", exc)

        for doc in relevant_docs:
            if doc.get("document"):
                verified_context_parts.append(doc["document"])

        if not verified_context_parts:
            context_str = "No specific government schemes found matching this query in the verified database."
        else:
            context_str = "\n\n---\n\n".join(verified_context_parts)

        # 3. Grounded fallback when Groq is not available
        if not self.provider.is_available():
            if scheme_data:
                s_name = scheme_data.get("name_hi") if lang_hi and scheme_data.get("name_hi") else scheme_data.get("name")
                benefits = scheme_data.get("benefits", [])
                docs = scheme_data.get("documents", [])
                official_url = scheme_data.get("official_url", "")
                if lang_hi:
                    ans = f"### {s_name} - सत्यापित सरकारी विवरण\n\n"
                    if benefits:
                        ans += "**मुख्य लाभ:**\n" + "\n".join(f"- {b}" for b in benefits) + "\n\n"
                    if docs:
                        ans += "**आवश्यक दस्तावेज़:**\n" + "\n".join(f"- {d}" for d in docs) + "\n\n"
                    ans += f"**आधिकारिक पोर्टल:** [{official_url}]({official_url})"
                else:
                    ans = f"### {s_name} - Verified Government Information\n\n"
                    if benefits:
                        ans += "**Key Benefits:**\n" + "\n".join(f"- {b}" for b in benefits) + "\n\n"
                    if docs:
                        ans += "**Required Documents:**\n" + "\n".join(f"- {d}" for d in docs) + "\n\n"
                    ans += f"**Official Portal:** [{official_url}]({official_url})"
                return {
                    "question": question,
                    "answer": ans,
                    "language": language,
                    "grounded_references": [{
                        "scheme_id": scheme_data["id"],
                        "category": scheme_data["category"],
                        "official_url": scheme_data["official_url"],
                    }],
                }
            return {
                "question": question,
                "answer": (
                    "ℹ️ **Verified Government Information:**\n\n"
                    "All scheme criteria, benefits, and application processes shown above are retrieved directly from official government databases. "
                    "(To activate conversational AI explanations with Groq, configure `GROQ_API_KEY` in your `.env` file.)"
                ),
                "language": language,
                "grounded_references": [],
            }

        # 4. Call Groq provider with strict grounding prompt
        system_prompt = SYSTEM_GROUNDING_PROMPT.format(context=context_str)
        user_prompt = f"Citizen Question: {question}\nLanguage: {'Hindi' if lang_hi else 'English'}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        answer = await self.provider.generate_response(messages)

        # 5. Extract references
        references = []
        if scheme_data:
            references.append({
                "scheme_id": scheme_data["id"],
                "category": scheme_data["category"],
                "official_url": scheme_data["official_url"],
            })
        for doc in relevant_docs:
            if doc.get("scheme_id") and not any(r["scheme_id"] == doc["scheme_id"] for r in references):
                references.append({
                    "scheme_id": doc["scheme_id"],
                    "category": doc.get("metadata", {}).get("category", ""),
                    "official_url": doc.get("metadata", {}).get("official_url", ""),
                })

        return {
            "question": question,
            "answer": answer,
            "language": language,
            "grounded_references": references,
        }


ai_service = AIService()

