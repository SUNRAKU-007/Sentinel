# ============================================================
# src/report_generator.py
# SENTINEL REPORT GENERATOR
# ============================================================

from collections import Counter


# ============================================================
# HELPERS
# ============================================================

def get_value(data, *keys, default=None):
    """
    Safely get the first available value from a dictionary.
    """
    for key in keys:
        if key in data:
            return data[key]

    return default


def money(value):
    """
    Format monetary values cleanly.
    """
    if value is None:
        return "₹0.00"

    return f"₹{value:,.2f}"


def percentage(value):
    """
    Convert decimal percentage to readable percentage.
    """
    if value is None:
        return "N/A"

    return f"{value * 100:.2f}%"


# ============================================================
# INCIDENT INFORMATION
# ============================================================

def extract_incident_stats(incident):
    """
    Extract useful information from an investigated incident.
    """

    total_transactions = get_value(
        incident,
        "total_transactions",
        default=0
    )

    failed_transactions = get_value(
        incident,
        "failed_transactions",
        default=0
    )

    total_value = get_value(
        incident,
        "total_transaction_value",
        default=0.0
    )

    failed_value = get_value(
        incident,
        "failed_transaction_value",
        default=0.0
    )

    observed_rate = get_value(
        incident,
        "observed_failure_rate"
    )

    baseline_rate = get_value(
        incident,
        "baseline_failure_rate"
    )

    z_score = get_value(
        incident,
        "peak_z_score",
        "z_score"
    )

    primary_reason = get_value(
        incident,
        "primary_failure_reason",
        default="unknown"
    )

    contribution = get_value(
        incident,
        "primary_reason_contribution",
        default=0.0
    )

    severity = get_value(
        incident,
        "severity",
        default="UNKNOWN"
    )

    return {
        "total_transactions": total_transactions,
        "failed_transactions": failed_transactions,
        "total_value": total_value,
        "failed_value": failed_value,
        "observed_rate": observed_rate,
        "baseline_rate": baseline_rate,
        "z_score": z_score,
        "primary_reason": primary_reason,
        "contribution": contribution,
        "severity": severity
    }


# ============================================================
# BUILD SUMMARY
# ============================================================

def build_summary(results):
    """
    Build overall Sentinel statistics.
    """

    analyses = results.get(
        "analyses",
        []
    )

    total_transactions = len(
        results.get("data", [])
    )

    anomalies = len(
        results.get("anomalies", [])
    )

    incidents = len(
        results.get("incidents", [])
    )

    investigated = len(
        results.get("investigated_incidents", [])
    )

    total_failed = 0
    total_failed_value = 0.0

    severities = Counter()
    failure_reasons = Counter()

    for result in analyses:

        analysis = result.get(
            "analysis",
            {}
        )

        if not isinstance(analysis, dict):
            continue

        impact = analysis.get(
            "business_impact",
            {}
        )

        failed = impact.get(
            "failed_transactions",
            0
        )

        failed_value = impact.get(
            "failed_transaction_value",
            0.0
        )

        total_failed += failed
        total_failed_value += failed_value

        severity = analysis.get(
            "severity",
            "UNKNOWN"
        )

        severities[severity] += 1

        reason_data = analysis.get(
            "primary_failure_reason",
            {}
        )

        if isinstance(reason_data, dict):

            reason = reason_data.get(
                "reason"
            )

            if reason:
                failure_reasons[reason] += 1

    return {
        "total_transactions": total_transactions,
        "anomalies": anomalies,
        "incidents": incidents,
        "investigated": investigated,
        "failed_transactions": total_failed,
        "failed_value": total_failed_value,
        "severities": severities,
        "failure_reasons": failure_reasons
    }


# ============================================================
# PRINT HEADER
# ============================================================

def print_header(title):

    print("\n" + "=" * 60)
    print(
        f"{title:^60}"
    )
    print("=" * 60)


# ============================================================
# PRINT OVERALL SUMMARY
# ============================================================

def print_overall_summary(summary):

    print_header(
        "SENTINEL INCIDENT REPORT"
    )

    print(
        f"\nTotal Transactions       : "
        f"{summary['total_transactions']:,}"
    )

    print(
        f"Anomalies Detected       : "
        f"{summary['anomalies']}"
    )

    print(
        f"Incidents                : "
        f"{summary['incidents']}"
    )

    print(
        f"Investigated             : "
        f"{summary['investigated']}"
    )

    print(
        f"Failed Transactions      : "
        f"{summary['failed_transactions']}"
    )

    print(
        f"Failed Transaction Value : "
        f"{money(summary['failed_value'])}"
    )


# ============================================================
# PRINT SEVERITY SUMMARY
# ============================================================

def print_severity_summary(summary):

    print_header(
        "INCIDENT SEVERITY"
    )

    severities = summary["severities"]

    for severity in [
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
        "UNKNOWN"
    ]:

        count = severities.get(
            severity,
            0
        )

        if count:
            print(
                f"{severity:<12} : {count}"
            )


# ============================================================
# PRINT FAILURE REASONS
# ============================================================

def print_failure_reasons(summary):

    print_header(
        "PRIMARY FAILURE REASONS"
    )

    reasons = summary["failure_reasons"]

    if not reasons:
        print("No failure reason data available.")
        return

    for reason, count in reasons.most_common():

        print(
            f"{reason:<22} : {count} incident(s)"
        )


# ============================================================
# PRINT INCIDENT
# ============================================================

def print_incident(index, result):

    incident = result.get(
        "incident",
        {}
    )

    analysis = result.get(
        "analysis",
        {}
    )

    print_header(
        f"SENTINEL INCIDENT {index}"
    )

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    payment_method = get_value(
        incident,
        "payment_method",
        "method",
        default="UNKNOWN"
    )

    bank = get_value(
        incident,
        "bank",
        "bank_issuer",
        "affected_bank",
        "processing_bank",
        default="UNKNOWN"
    )

    print(
        f"\nPayment Method : {payment_method}"
    )

    print(
        f"Bank           : {bank}"
    )

    # --------------------------------------------------------
    # Analysis
    # --------------------------------------------------------

    if isinstance(analysis, dict):

        summary = analysis.get(
            "incident_summary",
            "No summary available."
        )

        why_anomaly = analysis.get(
            "why_anomaly",
            "No anomaly explanation available."
        )

        print(
            f"\nSUMMARY\n"
            f"{summary}"
        )

        print(
            f"\nWHY THIS IS AN ANOMALY\n"
            f"{why_anomaly}"
        )

        # ----------------------------------------------------
        # Failure reason
        # ----------------------------------------------------

        reason_data = analysis.get(
            "primary_failure_reason",
            {}
        )

        if isinstance(reason_data, dict):

            reason = reason_data.get(
                "reason",
                "UNKNOWN"
            )

            contribution = reason_data.get(
                "contribution",
                0.0
            )

            print(
                f"\nPRIMARY FAILURE REASON\n"
                f"Reason        : {reason}\n"
                f"Contribution  : "
                f"{contribution * 100:.2f}%"
            )

        # ----------------------------------------------------
        # Business impact
        # ----------------------------------------------------

        impact = analysis.get(
            "business_impact",
            {}
        )

        print(
            "\nBUSINESS IMPACT"
        )

        print(
            f"Total Transactions : "
            f"{impact.get('total_transactions', 0):,}"
        )

        print(
            f"Failed Transactions : "
            f"{impact.get('failed_transactions', 0):,}"
        )

        print(
            f"Attempted Value : "
            f"{money(impact.get('total_transaction_value', 0))}"
        )

        print(
            f"Failed Value    : "
            f"{money(impact.get('failed_transaction_value', 0))}"
        )

        # ----------------------------------------------------
        # Investigation
        # ----------------------------------------------------

        print(
            "\nRECOMMENDED INVESTIGATION"
        )

        recommendations = analysis.get(
            "recommended_investigation",
            []
        )

        for i, recommendation in enumerate(
            recommendations,
            start=1
        ):

            print(
                f"{i}. {recommendation}"
            )

        # ----------------------------------------------------
        # Severity
        # ----------------------------------------------------

        severity = analysis.get(
            "severity",
            "UNKNOWN"
        )

        print(
            f"\nSEVERITY : {severity}"
        )

    else:

        print(
            "\nAI analysis is not available."
        )


# ============================================================
# GENERATE COMPLETE REPORT
# ============================================================

def generate_report(results):

    summary = build_summary(
        results
    )

    print_overall_summary(
        summary
    )

    print_severity_summary(
        summary
    )

    print_failure_reasons(
        summary
    )

    for index, result in enumerate(
        results.get("analyses", []),
        start=1
    ):

        print_incident(
            index,
            result
        )

    print_header(
        "END OF SENTINEL REPORT"
    )

    return summary