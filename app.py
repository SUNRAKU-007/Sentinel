import streamlit as st
from src.pipeline import run_pipeline


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sentinel",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ Sentinel")
st.subheader("AI-Powered Payment Anomaly & Incident Analysis")

st.markdown(
    """
    Sentinel detects unusual payment failure patterns,
    groups related anomalies into incidents, investigates their
    business impact, and uses Gemini AI to analyze the incidents.
    """
)


# ============================================================
# RUN SENTINEL
# ============================================================

if st.button("🚀 Run Sentinel", type="primary"):

    with st.spinner("Running Sentinel pipeline..."):

        results = run_pipeline()

    # ========================================================
    # EXTRACT RESULTS
    # ========================================================

    data = results.get(
        "data",
        []
    )

    anomalies = results.get(
        "anomalies",
        []
    )

    incidents = results.get(
        "incidents",
        []
    )

    investigated = results.get(
        "investigated_incidents",
        []
    )

    analyses = results.get(
        "analyses",
        []
    )

    # ========================================================
    # SYSTEM OVERVIEW
    # ========================================================

    st.divider()

    st.header("📊 System Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Transactions",
        f"{len(data):,}"
    )

    col2.metric(
        "Anomalies",
        len(anomalies)
    )

    col3.metric(
        "Incidents",
        len(incidents)
    )

    col4.metric(
        "Investigated",
        len(investigated)
    )

    # ========================================================
    # INCIDENTS
    # ========================================================

    st.divider()

    st.header("🚨 Detected Incidents")

    if not analyses:

        st.info("No incidents detected.")

    else:

        for index, result in enumerate(
            analyses,
            start=1
        ):

            incident = result.get(
                "incident",
                {}
            )

            analysis = result.get(
                "analysis",
                {}
            )

            with st.expander(
                f"Incident #{index}",
                expanded=index == 1
            ):

                # ====================================================
                # BASIC INCIDENT INFORMATION
                # ====================================================

                col1, col2, col3 = st.columns(3)

                # IMPORTANT:
                # Some parts of the pipeline use "method"
                # while others use "payment_method".
                # Check both so the dashboard doesn't show UNKNOWN.

                payment_method = incident.get(
                    "payment_method",
                    incident.get(
                        "method",
                        "UNKNOWN"
                    )
                )

                bank = incident.get(
                    "bank",
                    incident.get(
                        "bank_issuer",
                        incident.get(
                            "affected_bank",
                            incident.get(
                                "processing_bank",
                                "UNKNOWN"
                            )
                        )
                    )
                )

                severity = analysis.get(
                    "severity",
                    incident.get(
                        "severity",
                        "UNKNOWN"
                    )
                )

                col1.metric(
                    "Payment Method",
                    payment_method
                )

                col2.metric(
                    "Bank",
                    bank
                )

                col3.metric(
                    "Severity",
                    severity
                )

                # ====================================================
                # SUMMARY
                # ====================================================

                st.subheader("Summary")

                st.write(
                    analysis.get(
                        "incident_summary",
                        "No summary available."
                    )
                )

                # ====================================================
                # WHY ANOMALY
                # ====================================================

                st.subheader(
                    "Why This Is An Anomaly"
                )

                st.write(
                    analysis.get(
                        "why_anomaly",
                        "No explanation available."
                    )
                )

                # ====================================================
                # PRIMARY FAILURE REASON
                # ====================================================

                reason_data = analysis.get(
                    "primary_failure_reason",
                    {}
                )

                if isinstance(
                    reason_data,
                    dict
                ):

                    st.subheader(
                        "Primary Failure Reason"
                    )

                    col1, col2 = st.columns(2)

                    reason = reason_data.get(
                        "reason",
                        "UNKNOWN"
                    )

                    contribution = reason_data.get(
                        "contribution",
                        0.0
                    )

                    col1.write(
                        f"**Reason:** {reason}"
                    )

                    col2.write(
                        f"**Contribution:** "
                        f"{contribution * 100:.2f}%"
                    )

                # ====================================================
                # BUSINESS IMPACT
                # ====================================================

                impact = analysis.get(
                    "business_impact",
                    {}
                )

                st.subheader(
                    "💰 Business Impact"
                )

                col1, col2, col3, col4 = st.columns(4)

                total_transactions = impact.get(
                    "total_transactions",
                    0
                )

                failed_transactions = impact.get(
                    "failed_transactions",
                    0
                )

                transaction_value = impact.get(
                    "total_transaction_value",
                    0
                )

                failed_value = impact.get(
                    "failed_transaction_value",
                    0
                )

                col1.metric(
                    "Transactions",
                    f"{total_transactions:,}"
                )

                col2.metric(
                    "Failed",
                    f"{failed_transactions:,}"
                )

                col3.metric(
                    "Transaction Value",
                    f"₹{transaction_value:,.2f}"
                )

                col4.metric(
                    "Failed Value",
                    f"₹{failed_value:,.2f}"
                )

                # ====================================================
                # INVESTIGATION
                # ====================================================

                st.subheader(
                    "🔎 Recommended Investigation"
                )

                recommendations = analysis.get(
                    "recommended_investigation",
                    []
                )

                if recommendations:

                    for recommendation in recommendations:

                        st.write(
                            f"• {recommendation}"
                        )

                else:

                    st.write(
                        "No investigation recommendations available."
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Sentinel • Payment Reliability & Incident Analysis"
)