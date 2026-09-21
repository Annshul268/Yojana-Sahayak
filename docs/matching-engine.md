# Deterministic Matching Engine Specification

## Core Principle
The eligibility engine evaluates deterministic rules strictly before any AI interaction. An LLM cannot override, bypass, or invent rules.

## Eligibility Statuses
1. **`Eligible`**: All mandatory hard criteria (age, income ceiling, state, gender, social category) are fully satisfied by the user's profile.
2. **`Potentially Eligible`**: User meets known criteria, but some specific sub-criteria require manual confirmation or missing data.
3. **`Not Eligible`**: At least one mandatory hard criterion explicitly fails.

## Evaluation Structure
```json
{
  "scheme_id": "pm-kisan",
  "status": "potentially_eligible",
  "score": 85,
  "matched_rules": [
    { "rule": "occupation", "required": ["farmer"], "user_value": "farmer" },
    { "rule": "state", "required": ["ALL"], "user_value": "Uttar Pradesh" }
  ],
  "failed_rules": [],
  "missing_information": [
    { "field": "landholding_hectares", "reason": "Requires proof of agricultural landholding up to 2 hectares" }
  ]
}
```
