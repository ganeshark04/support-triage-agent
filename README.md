# Multi-Domain Support Triage Agent

## Overview

This project implements a terminal-based support triage agent capable of handling support tickets across multiple ecosystems:

* HackerRank Support
* Claude Help Center
* Visa Support

The agent processes incoming tickets, classifies them, evaluates risk, and determines whether to respond directly or escalate to human support.

---

## Features

* Multi-domain support (HackerRank, Claude, Visa)
* Request type classification (product_issue, bug, feature_request)
* Product area detection (billing, account_access, assessments, api, general)
* Risk detection and escalation for sensitive issues
* Support corpus matching using keyword-based retrieval
* Structured CSV output generation

---

## Architecture

The system follows a simple triage pipeline:

```text id="arch1"
Input CSV
   ↓
Preprocessing (merge subject + issue)
   ↓
Request Classification
   ↓
Risk Detection (escalation logic)
   ↓
Domain Inference
   ↓
Corpus Matching
   ↓
Response Generation
   ↓
Output CSV
```

---

## Input

The agent reads from:

```text id="input1"
support_tickets.csv
```

Each row contains:

* issue
* subject
* company

---

## Output

The agent generates:

```text id="output1"
output.csv
```

With the following fields:

* status (replied / escalated)
* product_area
* response
* justification
* request_type

---

## Escalation Logic

Tickets are escalated when high-risk indicators are detected, such as:

* fraud
* unauthorized access
* hacked accounts
* duplicate charges

---

## Quick Start

Run the agent:

```bash id="run1"
python triage.py
```

Make sure `support_tickets.csv` is present in the same directory.

---

## Project Structure

```text id="struct1"
.
├── triage.py
├── support_tickets.csv
├── output.csv
└── README.md
```

---

## Design Approach

* Rule-based classification for reliability
* Keyword-based corpus matching for simplicity
* Safety-first design for handling sensitive issues
* Deterministic outputs for consistent evaluation

---

## Notes

* CSV files do not store formatting; alignment issues in Excel are visual only
* Use "Wrap Text" in Excel for better readability

---

## Submission

This project was developed as part of the Multi-Domain Support Triage Challenge.

---

## Author

Hackathon submission
