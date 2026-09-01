# 🛡️ SENTINEL

# AI-Powered Payment Anomaly & Incident Analysis System

> **Detect with data. Explain with AI.**

Sentinel is an AI-powered payment reliability and incident analysis system designed to detect unusual payment failure patterns, group related anomalies into meaningful incidents, investigate their business impact, and use Google's Gemini LLM to generate concise and actionable incident analysis.

The core idea behind Sentinel is simple:

> **Payment failures are easy to detect. Understanding whether they represent a real incident is the difficult part.**

Sentinel combines statistical anomaly detection, incident correlation, deterministic investigation, and LLM-powered analysis into a single end-to-end pipeline.

---

# 📌 Table of Contents

- [🧩 Problem Statement](#-problem-statement)
- [💡 Why Sentinel](#-why-sentinel)
- [🎯 Project Objectives](#-project-objectives)
- [🏛️ Architecture](#️-architecture)
- [📊 What Sentinel Provides](#-what-sentinel-provides)
- [📁 Project Structure](#-project-structure)
- [🛠️ Technology Stack](#️-technology-stack)
- [🚧 Problems I Faced & Solutions](#-problems-i-faced--solutions)
- [🚀 Future Scope](#-future-scope)
---

# 🧩 Problem Statement

Modern payment systems process thousands or millions of transactions every day.

With such a large number of transactions, payment failures are inevitable. A small percentage of failed transactions can be normal system behavior.

However, the difficult problem begins when the failure pattern changes unexpectedly.

For example, suppose a payment system normally has a failure rate of around 4%.

Suddenly, during a particular time window:

```text
Normal Failure Rate
       ↓
       4%

       ↓

Observed Failure Rate
       ↓
      18%
```

That change may indicate a larger reliability problem affecting a particular bank, payment method, or failure reason.

The real problem is therefore not simply:

> **"Did a payment fail?"**

The important questions are:

- Did something unusual happen?
- Is the change statistically significant?
- Is the anomaly isolated or part of a larger pattern?
- Are multiple anomalies related to the same incident?
- Which payment method or bank is affected?
- What failure reason contributes the most?
- How many transactions were affected?
- How much transaction value was affected?
- What should an engineer investigate next?

Traditional monitoring systems can generate alerts when thresholds are crossed, but an alert by itself does not provide the complete context required for investigation.

An engineer may still need to inspect the data, identify the affected segment, determine the scale of the problem, and understand its business impact.

Sentinel was built to reduce this investigation gap.

---

# 💡 Why Sentinel

Sentinel does not treat anomaly detection as the end of the process.

Instead, it combines detection, investigation, and AI-assisted explanation.

The system aims to move from:

```text
"Something looks wrong."
```

to:

```text
"This payment segment is behaving unusually,
these transactions are affected,
this is the primary observed failure reason,
this is the business impact,
and these are the next investigation steps."
```

The important idea is the separation between **what the data proves** and **what the AI explains**.

The deterministic pipeline calculates the actual transaction and business metrics.

The LLM receives those results and converts them into a concise incident analysis.

This makes Sentinel an incident-analysis system rather than just another alert generator.

---

# 🎯 Project Objectives

The main objectives of Sentinel are:

### 1. Detect unusual payment behavior

Identify payment segments whose failure behavior deviates significantly from expected behavior.

### 2. Identify meaningful incidents

Group related anomalies instead of treating every anomaly as a completely independent problem.

### 3. Investigate incidents

Use transaction-level information to understand what happened and which parts of the payment system were affected.

### 4. Quantify business impact

Calculate:

- Total transactions
- Failed transactions
- Total transaction value
- Failed transaction value

### 5. Identify primary failure reasons

Determine which observed failure reason contributes most strongly to an incident.

### 6. Generate AI-assisted explanations

Use Google's Gemini LLM to turn structured incident data into a human-readable analysis.

### 7. Keep AI grounded

Prevent the LLM from inventing unsupported causes or business metrics.

### 8. Provide a usable interface

Expose the complete pipeline through a Streamlit dashboard that can be demonstrated easily.

---

# 🏛️ Architecture

Sentinel follows a modular pipeline architecture.

```text
                    ┌─────────────────────┐
                    │   Transaction Data  │
                    │    Data Generator   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Anomaly Detection   │
                    │ Statistical Engine  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Incident Detection  │
                    │ Correlation Layer   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Investigation    │
                    │  Business Impact    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Gemini LLM     │
                    │   Analysis Engine   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Streamlit Dashboard │
                    │  Incident Reports   │
                    └─────────────────────┘
```

---

# 📊 What Sentinel Provides

Sentinel transforms transaction-level data into an incident-level view.

Instead of only showing:

```text
Payment Failed
```

the system aims to provide:

```text
Incident
   ↓
Affected Segment
   ↓
Anomalous Behavior
   ↓
Primary Failure Reason
   ↓
Business Impact
   ↓
Severity
   ↓
Recommended Investigation
```

This provides more context to someone investigating payment reliability.

The output combines quantitative information from the analysis pipeline with qualitative explanation from the LLM.

---

# 📁 Project Structure

```text
Sentinel/
│
├── app.py
├── requirements.txt
├── README.md
│
└── src/
    ├── __init__.py
    ├── data_generator.py
    ├── anomaly_detector.py
    ├── incident_detector.py
    ├── investigation.py
    ├── llm_engine.py
    ├── pipeline.py
    └── report_generator.py
```

### Main Components

| File | Responsibility |
|------|----------------|
| `app.py` | Streamlit user interface |
| `pipeline.py` | Orchestrates the complete pipeline |
| `data_generator.py` | Generates transaction data |
| `anomaly_detector.py` | Detects anomalous payment behavior |
| `incident_detector.py` | Groups anomalies into incidents |
| `investigation.py` | Investigates incidents and calculates impact |
| `llm_engine.py` | Gemini-powered incident analysis |
| `report_generator.py` | Report generation utilities |
| `requirements.txt` | Python dependencies |

---

# 🛠️ Technology Stack

### Programming Language

- Python

### Data Processing

- Pandas
- NumPy

### AI / LLM

- Google Gemini API
- `google-genai`

### Application

- Streamlit

### Development Tools

- VS Code
- Git
- GitHub

### Deployment

- Streamlit Community Cloud

---

# 🚧 Problems I Faced & Solutions

Building Sentinel involved several practical problems beyond writing the core detection logic.

These challenges were important because the project had to work not only locally, but also with an external LLM API and a cloud deployment environment.

---

## 1. Detecting Real Anomalies

### Problem

A simple fixed threshold for payment failures can produce poor results.

For example:

```text
failure_rate > 10%
```

does not necessarily mean that the payment system is experiencing an unusual event.

Different segments can have different normal behavior.

### Solution

Sentinel uses statistical analysis to identify unusual payment behavior rather than relying only on a hard-coded failure threshold.

This makes anomaly detection more data-driven.

---

## 2. Anomaly vs Incident

### Problem

An anomaly does not automatically represent a separate incident.

Several anomalous observations can be related to the same underlying event.

Treating each one independently could create unnecessary alert noise.

### Solution

Sentinel introduces a separate incident detection stage that groups related anomalies into incidents.

```text
Anomalies
    ↓
Correlation
    ↓
Incidents
```

This allows the rest of the pipeline to operate at the incident level.

---

## 3. LLM Hallucination

### Problem

An LLM can produce plausible explanations that are not actually supported by the available data.

For example, if the data only says that failures increased, the model should not confidently claim:

```text
"The bank's server was down."
```

unless there is evidence for that conclusion.

### Solution

The LLM prompt explicitly tells Gemini to:

- Use only the provided incident data.
- Never invent causes.
- Distinguish facts from possible explanations.
- Avoid unsupported claims.
- Phrase recommendations as investigation steps.

This keeps the AI layer grounded in the deterministic analysis.

---

## 4. Gemini API Rate Limits

### Problem

During development, Gemini returned:

```text
429 RESOURCE_EXHAUSTED
```

The API itself was reachable, but the available free-tier request quota had been exceeded.

This was especially noticeable while repeatedly testing the pipeline.

### Solution

The LLM engine includes:

- Retry handling
- Request delays
- Fallback analysis

This means the application can continue functioning even when Gemini temporarily cannot accept another request.

---

## 5. Gemini Authentication

### Problem

At one stage, the Gemini client was initialized without correctly using the API key, resulting in:

```text
401 UNAUTHENTICATED
```

### Solution

The API key was configured through an environment variable and explicitly passed to the Gemini client.

The key was kept outside the source code rather than hard-coded into the project.

---

## 6. Streamlit Deployment Secrets

### Problem

The application worked locally because the local environment had access to the Gemini API key.

After deploying to Streamlit Cloud, the deployed environment did not automatically have access to local environment variables.

This caused the Gemini client to fail during application startup.

### Solution

The Gemini API key was added to Streamlit Secrets.

This allows the deployed application to access the credential without placing the secret inside GitHub source code.

---

# 🚀 Future Scope

Sentinel is currently a prototype for payment anomaly and incident analysis.

There are several directions in which it could be expanded.

---

## 1. Real Payment Data

The current system can be extended from generated transaction data to real payment datasets.

Possible sources could include:

- Payment gateway APIs
- Transaction databases
- Data warehouses
- Payment logs
- Event streams

---

## 2. Real-Time Monitoring

A future version could continuously process incoming transactions instead of requiring a manual pipeline run.

```text
Live Transactions
       ↓
Real-Time Detection
       ↓
Incident Detection
       ↓
Investigation
       ↓
AI Analysis
       ↓
Alert
```

This would move Sentinel toward real-time payment reliability monitoring.

---

## 3. Historical Baselines

Sentinel could maintain historical behavior for different payment segments.

For example:

```text
Bank A
    ↓
Historical Failure Rate

Payment Method X
    ↓
Historical Failure Rate
```

New observations could then be compared against historical baselines.

---

## 4. Smarter Incident Correlation

Incident detection could eventually consider more dimensions, including:

```text
Bank
Payment Method
Gateway
Region
Time
Failure Reason
Merchant
Device
```

This could help detect more complex incidents.

---

## 5. Automated Root-Cause Investigation

Future versions could connect Sentinel to:

- Application logs
- Gateway logs
- Server metrics
- Deployment history
- Infrastructure monitoring

The system could then compare payment incidents with other system events.

---

## 6. Automated Alerts

Sentinel could send incident notifications through:

- Slack
- Email
- Microsoft Teams
- PagerDuty

For example:

```text
🚨 HIGH SEVERITY PAYMENT INCIDENT

Payment Method: UPI
Affected Segment: XYZ

Failure Rate: 18%
Normal Rate: 4%

Failed Transaction Value: ₹X

Recommended Investigation:
Inspect gateway and payment integration logs.
```

---

## 7. Incident History

A database could be added to maintain historical incidents.

This could allow engineers to search for:

- Previous incidents
- Similar incidents
- Recurring failure reasons
- Frequently affected payment segments
- Incident frequency
- Recovery time

---

## 8. Incident Similarity

A future AI or vector-search layer could compare new incidents with historical incidents.

```text
New Incident
     ↓
Similarity Search
     ↓
Previous Similar Incident
     ↓
Previous Investigation
     ↓
Suggested Investigation Path
```

This could reduce investigation time for recurring problems.

---

## 9. Improved Severity Scoring

Future versions could calculate severity using multiple factors:

```text
Failure Rate
      +
Transaction Volume
      +
Financial Impact
      +
Duration
      +
Affected Segments
      +
Historical Frequency
```

This could provide a more comprehensive incident priority score.

---

# 👨‍💻 Author

**Manjot Singh**

AI-powered payment anomaly and incident analysis project.

---
