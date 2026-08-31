# ============================================================
# src/pipeline.py
# SENTINEL PIPELINE ORCHESTRATOR
# ============================================================

from src.data_generator import generate_data
from src.anomaly_detector import detect_anomalies
from src.incident_detector import detect_incidents
from src.investigation import investigate_incidents
from src.llm_engine import analyze_incidents


# ============================================================
# RUN COMPLETE SENTINEL PIPELINE
# ============================================================

def run_pipeline():

    # --------------------------------------------------------
    # 1. Generate transaction data
    # --------------------------------------------------------

    df = generate_data()

    print(f"Transactions: {len(df)}")


    # --------------------------------------------------------
    # 2. Detect anomalies
    # --------------------------------------------------------

    anomalies, segment_stats = detect_anomalies(df)

    print(f"Anomalies: {len(anomalies)}")


    # --------------------------------------------------------
    # 3. Group anomalies into incidents
    # --------------------------------------------------------

    incidents = detect_incidents(anomalies)

    print(f"Incidents: {len(incidents)}")


    # --------------------------------------------------------
    # 4. Investigate incidents
    # --------------------------------------------------------

    investigated_incidents = investigate_incidents(
        df,
        incidents
    )

    print(
        f"Investigated: "
        f"{len(investigated_incidents)}"
    )


    # --------------------------------------------------------
    # 5. Generate AI analysis
    # --------------------------------------------------------

    analyses = analyze_incidents(
        investigated_incidents
    )


    # --------------------------------------------------------
    # Return everything
    # --------------------------------------------------------

    return {
        "data": df,
        "anomalies": anomalies,
        "segment_stats": segment_stats,
        "incidents": incidents,
        "investigated_incidents": investigated_incidents,
        "analyses": analyses
    }