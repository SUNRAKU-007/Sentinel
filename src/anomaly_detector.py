# ============================================================
# src/anomaly_detector.py
# SENTINEL ANOMALY DETECTION ENGINE
# ============================================================

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

MIN_TRANSACTIONS = 10

BASELINE_WINDOWS = 6

MIN_BASELINE_POINTS = 3

MIN_ABSOLUTE_INCREASE = 0.15

MIN_Z_SCORE = 3.0

EPSILON = 1e-6


# ============================================================
# DETECT ANOMALIES
# ============================================================

def detect_anomalies(df):

    # ========================================================
    # 1. SEGMENT STATISTICS
    # ========================================================
    #
    # Segment =
    #
    # payment method + bank
    #
    # ========================================================

    segment_stats = (
        df
        .groupby(
            [
                "time_window",
                "method",
                "bank"
            ]
        )
        .agg(
            total_payments=(
                "payment_id",
                "count"
            ),

            failed_payments=(
                "status",
                lambda x:
                (x == "failed").sum()
            )
        )
        .reset_index()
    )


    # ========================================================
    # 2. FAILURE RATE
    # ========================================================

    segment_stats["failure_rate"] = (
        segment_stats["failed_payments"]
        /
        segment_stats["total_payments"]
    )


    # ========================================================
    # 3. SORT SEGMENTS
    # ========================================================

    segment_stats = (
        segment_stats
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
    # 4. HISTORICAL BASELINE
    # ========================================================
    #
    # Only PREVIOUS windows are used.
    #
    # The current window is excluded.
    #
    # ========================================================

    segment_stats[
        "baseline_failure_rate"
    ] = (
        segment_stats
        .groupby(
            [
                "method",
                "bank"
            ]
        )["failure_rate"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                window=BASELINE_WINDOWS,
                min_periods=MIN_BASELINE_POINTS
            )
            .mean()
        )
    )


    # ========================================================
    # 5. BASELINE STANDARD DEVIATION
    # ========================================================

    segment_stats[
        "baseline_std"
    ] = (
        segment_stats
        .groupby(
            [
                "method",
                "bank"
            ]
        )["failure_rate"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                window=BASELINE_WINDOWS,
                min_periods=MIN_BASELINE_POINTS
            )
            .std()
        )
    )


    # ========================================================
    # 6. FAILURE RATE INCREASE
    # ========================================================

    segment_stats[
        "failure_rate_increase"
    ] = (
        segment_stats["failure_rate"]
        -
        segment_stats["baseline_failure_rate"]
    )


    # ========================================================
    # 7. Z-SCORE
    # ========================================================

    segment_stats["z_score"] = (
        segment_stats["failure_rate_increase"]
        /
        (
            segment_stats["baseline_std"]
            +
            EPSILON
        )
    )


    # ========================================================
    # 8. INITIAL ANOMALY DETECTION
    # ========================================================

    segment_stats[
        "is_anomaly"
    ] = (
        (
            segment_stats["total_payments"]
            >= MIN_TRANSACTIONS
        )

        &

        (
            segment_stats["baseline_failure_rate"]
            .notna()
        )

        &

        (
            segment_stats["baseline_std"]
            .notna()
        )

        &

        (
            segment_stats["failure_rate_increase"]
            >= MIN_ABSOLUTE_INCREASE
        )

        &

        (
            segment_stats["z_score"]
            >= MIN_Z_SCORE
        )
    )


    # ========================================================
    # 9. CLEAN BASELINE
    # ========================================================
    #
    # Prevent anomalous windows from contaminating
    # future baselines.
    #
    # ========================================================

    segment_stats[
        "clean_baseline_failure_rate"
    ] = np.nan

    segment_stats[
        "clean_baseline_std"
    ] = np.nan

    segment_stats[
        "clean_z_score"
    ] = np.nan

    segment_stats[
        "clean_failure_increase"
    ] = np.nan


    # ========================================================
    # 10. PROCESS EACH METHOD + BANK
    # ========================================================

    for (
        method,
        bank
    ), group in segment_stats.groupby(
        [
            "method",
            "bank"
        ]
    ):

        group = (
            group
            .sort_values("time_window")
        )


        historical_rates = []


        # ====================================================
        # PROCESS WINDOWS
        # ====================================================

        for idx, row in group.iterrows():

            current_rate = (
                row["failure_rate"]
            )

            current_transactions = (
                row["total_payments"]
            )


            # ------------------------------------------------
            # Calculate clean baseline
            # ------------------------------------------------

            if (
                len(historical_rates)
                >=
                MIN_BASELINE_POINTS
            ):

                recent_history = (
                    historical_rates[
                        -BASELINE_WINDOWS:
                    ]
                )


                baseline = np.mean(
                    recent_history
                )


                baseline_std = np.std(
                    recent_history,
                    ddof=1
                )


                increase = (
                    current_rate
                    -
                    baseline
                )


                if baseline_std > 0:

                    z = (
                        increase
                        /
                        baseline_std
                    )

                else:

                    z = 0


                segment_stats.loc[
                    idx,
                    "clean_baseline_failure_rate"
                ] = baseline


                segment_stats.loc[
                    idx,
                    "clean_baseline_std"
                ] = baseline_std


                segment_stats.loc[
                    idx,
                    "clean_failure_increase"
                ] = increase


                segment_stats.loc[
                    idx,
                    "clean_z_score"
                ] = z


            # ------------------------------------------------
            # Decide anomaly
            # ------------------------------------------------

            is_anomaly = (

                current_transactions
                >=
                MIN_TRANSACTIONS

                and

                len(historical_rates)
                >=
                MIN_BASELINE_POINTS

                and

                baseline_std > 0

                and

                increase
                >=
                MIN_ABSOLUTE_INCREASE

                and

                z
                >=
                MIN_Z_SCORE
            )


            segment_stats.loc[
                idx,
                "is_anomaly"
            ] = is_anomaly


            # ------------------------------------------------
            # IMPORTANT:
            #
            # Do NOT add anomalous windows to history.
            # ------------------------------------------------

            if not is_anomaly:

                historical_rates.append(
                    current_rate
                )


    # ========================================================
    # 11. FINAL ANOMALIES
    # ========================================================

    anomalies = (
        segment_stats[
            segment_stats["is_anomaly"]
        ]
        .copy()
    )


    anomalies = (
        anomalies
        .sort_values(
            "clean_z_score",
            ascending=False
        )
        .reset_index(drop=True)
    )


    return anomalies, segment_stats