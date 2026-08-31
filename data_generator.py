# ============================================================
# src/data_generator.py
# SENTINEL PAYMENT DATA GENERATOR
# ============================================================

import numpy as np
import pandas as pd


# ============================================================
# 1. RANDOM SEED
# ============================================================

np.random.seed(42)


# ============================================================
# 2. BASIC CONFIGURATION
# ============================================================

N = 10_000

start_time = pd.Timestamp(
    "2026-08-30 09:00:00"
)

end_time = start_time + pd.Timedelta(
    hours=12
)


# ============================================================
# 3. GENERATE PAYMENT DATA
# ============================================================

def generate_data():

    # --------------------------------------------------------
    # Generate timestamps
    # --------------------------------------------------------

    timestamps = pd.to_datetime(
        np.random.uniform(
            start_time.value,
            end_time.value,
            N
        )
    )


    # --------------------------------------------------------
    # Generate transaction amounts
    # --------------------------------------------------------

    amounts = np.random.lognormal(
        mean=np.log(1500),
        sigma=0.8,
        size=N
    )

    amounts = np.round(
        amounts,
        2
    )


    # --------------------------------------------------------
    # Payment methods
    # --------------------------------------------------------

    methods = np.random.choice(
        [
            "UPI",
            "CARD",
            "NETBANKING"
        ],
        size=N,
        p=[
            0.55,
            0.30,
            0.15
        ]
    )


    # --------------------------------------------------------
    # Banks
    # --------------------------------------------------------

    banks = np.random.choice(
        [
            "HDFC",
            "SBI",
            "ICICI",
            "AXIS",
            "BANK_D"
        ],
        size=N,
        p=[
            0.25,
            0.20,
            0.20,
            0.20,
            0.15
        ]
    )


    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        {
            "payment_id": [
                f"pay_{i:06d}"
                for i in range(N)
            ],

            "timestamp": timestamps,

            "amount": amounts,

            "method": methods,

            "bank": banks
        }
    )


    # ========================================================
    # NORMAL SUCCESS PROBABILITY
    # ========================================================

    success_probability = {
        "UPI": 0.94,
        "CARD": 0.92,
        "NETBANKING": 0.89
    }


    random_values = np.random.random(N)


    df["success_probability"] = (
        df["method"].map(
            success_probability
        )
    )


    # ========================================================
    # SYNTHETIC INCIDENT
    # ========================================================

    incident_start = pd.Timestamp(
        "2026-08-30 11:30:00"
    )

    incident_end = pd.Timestamp(
        "2026-08-30 12:15:00"
    )


    incident_mask = (
        (df["timestamp"] >= incident_start)
        &
        (df["timestamp"] < incident_end)
        &
        (df["bank"] == "BANK_D")
        &
        (df["method"] == "UPI")
    )


    # During the incident,
    # success probability drops.

    df.loc[
        incident_mask,
        "success_probability"
    ] = 0.55


    # ========================================================
    # GENERATE STATUS
    # ========================================================

    df["status"] = np.where(
        random_values < df["success_probability"],
        "success",
        "failed"
    )


    # ========================================================
    # FAILURE REASONS
    # ========================================================

    failure_reasons = [
        "timeout",
        "declined",
        "insufficient_funds",
        "technical_error"
    ]


    failure_probabilities = [
        0.45,
        0.30,
        0.20,
        0.05
    ]


    failed_mask = (
        df["status"] == "failed"
    )


    failed_count = (
        failed_mask.sum()
    )


    # Object dtype allows strings and None.

    df["failure_reason"] = pd.Series(
        [None] * N,
        dtype="object"
    )


    df.loc[
        failed_mask,
        "failure_reason"
    ] = np.random.choice(
        failure_reasons,
        size=failed_count,
        p=failure_probabilities
    )


    # ========================================================
    # CREATE TIME WINDOWS
    # ========================================================

    df = (
        df
        .sort_values("timestamp")
        .reset_index(drop=True)
    )


    df["time_window"] = (
        df["timestamp"]
        .dt.floor("15min")
    )


    return df