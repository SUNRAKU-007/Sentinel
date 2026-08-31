# ============================================================
# main.py
# SENTINEL
# ============================================================

from src.pipeline import run_pipeline
from src.report_generator import generate_report


def main():

    # --------------------------------------------------------
    # Run complete Sentinel pipeline
    # --------------------------------------------------------

    results = run_pipeline()

    # --------------------------------------------------------
    # Generate final Sentinel report
    # --------------------------------------------------------

    generate_report(
        results
    )


if __name__ == "__main__":
    main()