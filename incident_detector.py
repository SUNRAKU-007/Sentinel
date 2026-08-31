# ============================================================
# src/incident_detector.py
# SENTINEL INCIDENT DETECTION
# ============================================================

import pandas as pd


# ============================================================
# GROUP ANOMALIES INTO INCIDENTS
# ============================================================

def detect_incidents(anomalies):

    incidents = []

    if len(anomalies) == 0:
        return incidents


    # --------------------------------------------------------
    # Sort by method, bank and time
    # --------------------------------------------------------

    anomalies = (
        anomalies
        .sort_values(
            [
                "method",
                "bank",
                "time_window"
            ]
        )
        .reset_index(drop=True)
    )


    # ========================================================
    # PROCESS EACH METHOD + BANK
    # ========================================================

    for (
        method,
        bank
    ), group in anomalies.groupby(
        [
            "method",
            "bank"
        ]
    ):

        group = (
            group
            .sort_values("time_window")
            .reset_index(drop=True)
        )


        current_incident = []

        previous_time = None


        # ====================================================
        # PROCESS ANOMALOUS WINDOWS
        # ====================================================

        for _, row in group.iterrows():

            current_time = row["time_window"]


            # ------------------------------------------------
            # Continue current incident if windows are
            # consecutive 15-minute windows
            # ------------------------------------------------

            if (
                previous_time is None
                or
                current_time
                ==
                previous_time
                +
                pd.Timedelta(minutes=15)
            ):

                current_incident.append(row)


            else:

                # --------------------------------------------
                # Previous incident finished
                # --------------------------------------------

                incidents.append(
                    build_incident(
                        current_incident,
                        method,
                        bank
                    )
                )


                # Start new incident

                current_incident = [row]


            previous_time = current_time


        # ====================================================
        # ADD LAST INCIDENT
        # ====================================================

        if len(current_incident) > 0:

            incidents.append(
                build_incident(
                    current_incident,
                    method,
                    bank
                )
            )


    return incidents


# ============================================================
# BUILD INCIDENT OBJECT
# ============================================================

def build_incident(
    incident_rows,
    method,
    bank
):

    incident_df = pd.DataFrame(
        incident_rows
    )


    # --------------------------------------------------------
    # Find peak failure-rate row
    # --------------------------------------------------------

    peak_failure_row = (
        incident_df
        .loc[
            incident_df["failure_rate"]
            .idxmax()
        ]
    )


    # --------------------------------------------------------
    # Find peak Z-score row
    # --------------------------------------------------------

    peak_z_row = (
        incident_df
        .loc[
            incident_df["clean_z_score"]
            .idxmax()
        ]
    )


    # --------------------------------------------------------
    # Create structured incident
    # --------------------------------------------------------

    incident = {

        "method": method,

        "bank": bank,

        "start_time": str(
            incident_df["time_window"].min()
        ),

        "end_time": str(
            incident_df["time_window"].max()
        ),

        "windows_affected": int(
            len(incident_df)
        ),

        "peak_failure_rate": float(
            peak_failure_row["failure_rate"]
        ),

        "peak_failure_rate_time": str(
            peak_failure_row["time_window"]
        ),

        "peak_z_score": float(
            peak_z_row["clean_z_score"]
        ),

        "peak_z_score_time": str(
            peak_z_row["time_window"]
        ),

        "windows": []

    }


    # --------------------------------------------------------
    # Store every anomalous window
    # --------------------------------------------------------

    for _, row in incident_df.iterrows():

        incident["windows"].append(

            {

                "time_window": str(
                    row["time_window"]
                ),

                "total_transactions": int(
                    row["total_payments"]
                ),

                "failed_transactions": int(
                    row["failed_payments"]
                ),

                "failure_rate": float(
                    row["failure_rate"]
                ),

                "baseline_failure_rate": float(
                    row[
                        "clean_baseline_failure_rate"
                    ]
                ),

                "failure_rate_increase": float(
                    row[
                        "clean_failure_increase"
                    ]
                ),

                "z_score": float(
                    row["clean_z_score"]
                )

            }

        )


    return incident