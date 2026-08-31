# ============================================================
# src/llm_engine.py
# SENTINEL LLM ENGINE
# ============================================================

from google import genai
import json
import time


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "gemini-3.6-flash"

MAX_RETRIES = 1

# Delay between separate incident requests
REQUEST_DELAY = 1


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

client = genai.Client()


# ============================================================
# FALLBACK ANALYSIS
# ============================================================

def fallback_analysis(incident):

    return {
        "incident_summary": "LLM analysis unavailable.",

        "why_anomaly": (
            "Unable to generate LLM analysis. "
            "The anomaly was detected by the Sentinel "
            "statistical detection engine."
        ),

        "primary_failure_reason": {
            "reason": incident.get(
                "primary_failure_reason"
            ),
            "contribution": incident.get(
                "primary_reason_contribution",
                0.0
            )
        },

        "business_impact": {
            "total_transactions": incident.get(
                "total_transactions",
                0
            ),

            "failed_transactions": incident.get(
                "failed_transactions",
                0
            ),

            "total_transaction_value": incident.get(
                "total_transaction_value",
                0.0
            ),

            "failed_transaction_value": incident.get(
                "failed_transaction_value",
                0.0
            )
        },

        "recommended_investigation": [
            "Review the incident manually.",
            "Inspect the relevant payment and gateway logs.",
            "Monitor subsequent time windows for recovery."
        ],

        "severity": "MEDIUM"
    }


# ============================================================
# VALIDATE LLM RESPONSE
# ============================================================

def validate_analysis(result):

    required_fields = [
        "incident_summary",
        "why_anomaly",
        "primary_failure_reason",
        "business_impact",
        "recommended_investigation",
        "severity"
    ]

    # Check top-level fields
    for field in required_fields:
        if field not in result:
            return False

    # Check primary failure reason
    primary_reason = result.get(
        "primary_failure_reason"
    )

    if not isinstance(primary_reason, dict):
        return False

    if "reason" not in primary_reason:
        return False

    if "contribution" not in primary_reason:
        return False

    # Check business impact
    business_impact = result.get(
        "business_impact"
    )

    if not isinstance(business_impact, dict):
        return False

    required_impact_fields = [
        "total_transactions",
        "failed_transactions",
        "total_transaction_value",
        "failed_transaction_value"
    ]

    for field in required_impact_fields:
        if field not in business_impact:
            return False

    # Check investigation list
    if not isinstance(
        result["recommended_investigation"],
        list
    ):
        return False

    # Check severity
    if result["severity"] not in [
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    ]:
        return False

    return True


# ============================================================
# ANALYZE INCIDENT
# ============================================================

def analyze_incident(incident):

    incident_json = json.dumps(
        incident,
        indent=4,
        default=str
    )

    prompt = f"""
You are Sentinel, a payment reliability investigation assistant.

Analyze the following payment incident for a payment
operations engineer.

INCIDENT DATA:

{incident_json}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "incident_summary": "string",

    "why_anomaly": "string",

    "primary_failure_reason": {{
        "reason": "string or null",
        "contribution": 0.0
    }},

    "business_impact": {{
        "total_transactions": 0,
        "failed_transactions": 0,
        "total_transaction_value": 0.0,
        "failed_transaction_value": 0.0
    }},

    "recommended_investigation": [
        "string",
        "string",
        "string"
    ],

    "severity": "LOW"
}}

RULES:

1. Use ONLY information provided in INCIDENT DATA.

2. Do NOT invent causes.

3. Clearly distinguish observed facts from possible explanations.

4. If a cause is not present in the incident data,
   do not claim that it happened.

5. You may recommend checking something,
   but phrase it as an investigation step,
   not as a confirmed cause.

6. The primary failure reason and contribution must
   come directly from the provided data.

7. Business impact values must come directly from
   the provided data.

8. Severity must be one of:

   LOW
   MEDIUM
   HIGH
   CRITICAL

9. Keep the response concise.

10. Return JSON only.
"""

    # ========================================================
    # RETRY GEMINI REQUEST
    # ========================================================

    for attempt in range(MAX_RETRIES):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            # ------------------------------------------------
            # Extract response
            # ------------------------------------------------

            text = response.text.strip()

            # ------------------------------------------------
            # Parse JSON
            # ------------------------------------------------

            result = json.loads(text)

            # ------------------------------------------------
            # Validate structure
            # ------------------------------------------------

            if not validate_analysis(result):

                print(
                    "\nGemini returned invalid JSON structure."
                )

                return fallback_analysis(
                    incident
                )

            return result

        # ====================================================
        # TEMPORARY API ERROR
        # ====================================================

        except Exception as e:

            error_message = str(e)

            print(
                f"\nGemini request failed "
                f"(attempt {attempt + 1}/{MAX_RETRIES})"
            )

            print(
                f"Error: {error_message}"
            )

            # ------------------------------------------------
            # Retry if attempts remain
            # ------------------------------------------------

            if attempt < MAX_RETRIES - 1:

                wait_time = 2 ** attempt

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                print(
                    "Gemini unavailable. "
                    "Using fallback analysis."
                )

    # ========================================================
    # FALLBACK
    # ========================================================

    return fallback_analysis(
        incident
    )


# ============================================================
# ANALYZE MULTIPLE INCIDENTS
# ============================================================

def analyze_incidents(incidents):

    results = []

    total = len(incidents)

    for i, incident in enumerate(incidents):

        print(
            f"\nAnalyzing incident "
            f"{i + 1}/{total}..."
        )

        analysis = analyze_incident(
            incident
        )

        results.append(
            {
                "incident": incident,
                "analysis": analysis
            }
        )

        # ----------------------------------------------------
        # Delay between Gemini requests
        # ----------------------------------------------------

        if i < total - 1:

            time.sleep(
                REQUEST_DELAY
            )

    return results