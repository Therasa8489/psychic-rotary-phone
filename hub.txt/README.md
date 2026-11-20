# Nalla Chennai 🚦♻️
AI-powered traffic violation and litter detection with a fine + reward system.

## Problem
- Traffic rule violations and signal chaos need constant police monitoring.
- Roads are littered with plastic even where dustbins exist.

## Solution
Cameras detect violations (traffic + littering), identify the vehicle/person, send an alert, and allow online fine payment. Good behaviour (using bins) earns reward points.

## Roadmap
- [ ] Phase 1 (MVP): vehicle detection -> helmet / red light -> number plate OCR -> fine + SMS
- [ ] Phase 2: litter detection, rewards, citizen app
- [ ] Phase 3: adaptive signals, accident detection, analytics dashboard
- [ ] Phase 4: edge deployment, pilot proposal

## Data policy
Routine footage is auto-deleted within 30 days. Footage linked to violations, accidents or active disputes is kept in an evidence vault with legal hold, access logging and integrity hashing.

## Note
Demo uses simulated owner data. No real personal data is used.

## Quick start
```bash
cd ai-engine && pip install -r requirements.txt
python detect.py --source ../dataset/sample.mp4
cd ../backend && pip install -r requirements.txt
uvicorn main:app --reload
```
