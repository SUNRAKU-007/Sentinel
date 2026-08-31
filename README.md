# Sentinel

## AI-Powered Payment Anomaly & Incident Analysis

Sentinel is a prototype payment reliability system that detects unusual payment failure patterns, groups related anomalies into incidents, investigates their business impact, and uses Gemini to generate an incident analysis.

The project uses synthetic payment transaction data for demonstration purposes.

---

## Pipeline

```text
Synthetic Transaction Data
            ↓
    Anomaly Detection
            ↓
    Incident Detection
            ↓
       Investigation
            ↓
      Gemini AI Analysis
            ↓
      Incident Report
