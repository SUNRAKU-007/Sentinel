# ============================================================
# src/investigation.py
# SENTINEL ANOMALY INVESTIGATION ENGINE
# ============================================================

import pandas as pd


# ============================================================
# INVESTIGATE INCIDENTS
# ============================================================

def investigate_incidents(df, incidents):

    investigated_incidents = []

    for incident in incidents:

        method = incident["method"]
        bank = incident["bank"]

        start_time = pd.Timestamp(
            incident["start_time"]
        )

        end_time = pd.Timestamp(
            incident["end_time"]
        )

        # Include the complete final 15-minute window
        end_time_exclusive = (
            end_time + pd.Timedelta(minutes=15)
        )

        # ====================================================
        # GET TRANSACTIONS BELONGING TO INCIDENT
        # ====================================================

        incident_transactions = df[
            (df["method"] == method)
            &
            (df["bank"] == bank)
            &
            (df["time_window"] >= start_time)
            &
            (df["time_window"] < end_time_exclusive)
        ].copy()

        # ====================================================
        # FAILED TRANSACTIONS
        # ====================================================

        failed_transactions = (
            incident_transactions[
                incident_transactions["status"] == "failed"
            ]
        )

        # ====================================================
        # FAILURE REASONS
        # ====================================================

        reason_counts = (
            failed_transactions["failure_reason"]
            .value_counts()
            .to_dict()
        )

        # Convert NumPy integers to normal Python integers
        reason_counts = {
            str(reason): int(count)
            for reason, count in reason_counts.items()
        }

        # ====================================================
        # PRIMARY FAILURE REASON
        # ====================================================

        if len(reason_counts) > 0:

            primary_reason = max(
                reason_counts,
                key=reason_counts.get
            )

            primary_reason_count = (
                reason_counts[primary_reason]
            )

            if len(failed_transactions) > 0:

                primary_reason_contribution = (
                    primary_reason_count
                    /
                    len(failed_transactions)
                )

            else:

                primary_reason_contribution = 0.0

        else:

            primary_reason = None

            primary_reason_contribution = 0.0

        # ====================================================
        # BUSINESS IMPACT
        # ====================================================

        total_transactions = (
            len(incident_transactions)
        )

        failed_count = (
            len(failed_transactions)
        )

        total_value = float(
            incident_transactions["amount"].sum()
        )

        failed_value = float(
            failed_transactions["amount"].sum()
        )

        # ====================================================
        # ADD INVESTIGATION DATA
        # ====================================================

        investigated_incident = {
            **incident,

            "total_transactions": int(
                total_transactions
            ),

            "failed_transactions": int(
                failed_count
            ),

            "failure_reasons": reason_counts,

            "primary_failure_reason": (
                primary_reason
            ),

            "primary_reason_contribution": float(
                primary_reason_contribution
            ),

            "total_transaction_value": (
                total_value
            ),

            "failed_transaction_value": (
                failed_value
            )
        }

        investigated_incidents.append(
            investigated_incident
        )

    return investigated_incidents