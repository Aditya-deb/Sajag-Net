# SajagNet: Network Threat Detection and Risk Analysis

"Sajag" means alert or vigilant (Hindi/Sanskrit). SajagNet is a **prototype**, not a production security tool. It classifies network flows, explains each prediction, groups alerts into incidents, and ranks them by estimated business risk.

## What it does

CIC-IDS2017 flows -> cleaning and de-duplication -> LightGBM classifier (5 classes: Benign, DoS/DDoS, PortScan, Brute Force, Web Attack) -> SHAP explanations -> incident builder -> risk engine -> Streamlit dashboard.

## How this project was built

I designed, directed and tested this project. The code was written with AI coding assistants (Gemini, then Claude). I do not yet write code independently, and I checked results by recomputing numbers from raw outputs and running the test suite (25 tests).

## Data

- Dataset: CIC-IDS2017 (Sharafaldin, Lashkari, Ghorbani, ICISSP 2018), using the cleaned Kaggle variant `cicids2017_cleaned.csv` by Eric Anacleto Ribeiro. The dataset is not included in this repository.
- IP addresses, Flow ID, Timestamp and SimillarHTTP columns were dropped. Exact duplicates were removed before splitting (2,518,803 -> 2,496,016 rows).
- A capped subset of 147,143 rows was used (Benign 100,000; DoS/DDoS 30,000; PortScan 10,000; Brute Force 5,000; Web Attack 2,143).
- Random stratified 80/20 split; the test set is 29,429 flows.

## Results (held-out test set, from reports/metrics.json)

| Model | Accuracy | Macro-F1 | Macro PR-AUC | False alarms per 100k benign flows | Web Attack recall |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Decision Tree baseline (max depth 8) | 99.11% | 0.9776 | 0.9665 | 270 | 87.9% |
| LightGBM, no port columns (primary) | 99.84% | 0.9967 | 0.9993 | 130 | 99.1% |
| LightGBM, no ports and no TCP-window features | 98.14% | 0.9238 | 0.9916 | 2,365 | 96.3% |

Removing the TCP-window features (Init_Win_bytes_forward/backward, min_seg_size_forward) raised false alarms from 130 to 2,365 per 100k benign flows (about 18.2x). The model depends strongly on these features. This may partly reflect how the lab traffic was generated, but this project cannot show that.

## Limitations (please read)

- **Random split, not chronological.** The Timestamp column was dropped, so the split is not time-based. Scores are probably optimistic compared with real deployment.
- **The dataset is relatively easy.** A depth-8 Decision Tree already reaches 99.11%.
- **Lab data.** CIC-IDS2017 is synthetic lab traffic. Nothing here shows the model works on a real network.
- **Scores are not calibrated.** The "model score" is the raw LightGBM class probability. It should not be read as a true probability of attack.
- **Risk numbers are illustrative assumptions.** Severity, downtime hours, breach probabilities, asset values and costs are made-up inputs, not measured data.
- **Port columns are not model features.** Destination_Port is used only to look up the asset in the registry.
- **Tested environment:** developed and tested on Windows with Python 3.15.2 only.

## Risk engine (all inputs are assumptions)

- Exposure = confidence x (downtime_hours x hourly_cost + p_breach x breach_liability).
- Risk score = 100 x (0.40 x severity + 0.35 x asset criticality + 0.25 x model score).
- Cost rule: the rule holds if exposure > (1 - confidence) x cost of blocking.
- Action: Block & Remediate if the rule holds and confidence >= 0.90; Investigate if the rule holds and 0.50 <= confidence < 0.90; otherwise Log & Alert.
- Triage cost: $50 per alert.
- Threat classes are mapped to MITRE ATT&CK: Brute Force T1110, Web Attack T1190, DoS/DDoS T1498, PortScan T1046.

| Threat class | Severity (0-1) | Downtime (hours) | Breach probability |
| :--- | :--- | :--- | :--- |
| Brute Force | 0.7 | 0.0 | 5% |
| Web Attack | 0.8 | 1.0 | 15% |
| DoS/DDoS | 0.9 | 2.0 | 0% |
| PortScan | 0.4 | 0.0 | 2% |

| Port | Asset | Criticality (0-1) | Hourly downtime cost | Breach liability | Cost of blocking |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 80 | Public Web Server | 0.7 | $5,000 | $50,000 | $1,000 |
| 443 | Secure Web Gateway | 0.9 | $10,000 | $250,000 | $2,500 |
| 22 | Internal SSH/Admin | 1.0 | $2,000 | $500,000 | $500 |
| default | General Endpoint | 0.3 | $500 | $5,000 | $100 |

### Sensitivity of the ranking

The top-ranked incident in the sample is SSH Brute Force. Its rank depends on the assumed breach probability and liability (computed by the real code at model score 0.9999; see `reports/sensitivity.md`):

| Scenario | SSH Brute Force exposure | Rank among incidents |
| :--- | :--- | :--- |
| Baseline (5.0% breach probability, $500,000 liability) | $24,997.50 | #1 |
| Breach probability 2.5% | $12,498.75 | #1 (tie) |
| Breach probability 1.5% | $7,499.25 | #3 |
| Breach probability 7.5% | $37,496.25 | #1 |
| Liability -50% ($250,000) | $12,498.75 | #1 (tie) |
| Liability $150,000 | $7,499.25 | #3 |
| Liability +50% ($750,000) | $37,496.25 | #1 |

The SSH incident drops below the DoS incident when breach probability x liability is under $10,000.

## Dashboard

Run `streamlit run app\dashboard.py`, then click "Load Simulated Traffic Sample".

- Tab 1: a simulated stream of 1,000 held-out test flows, with SHAP explanations for a selected flow.
- Tab 2: incidents (flows grouped by class and mapped asset) with risk score, exposure, action and mitigation; a Decision Explorer; and a comparison of the primary model against the no-TCP model.

## Repository layout

- `app/dashboard.py`: Streamlit dashboard
- `src/sajagnet/`: config, preprocessing, risk engine, MITRE mapper, incident builder
- `scripts/`: data processing, training, evaluation, SHAP, sanity checks, sensitivity, table generation
- `tests/`: 25 tests
- `models/`, `reports/`, `DECISIONS.md`

## Reproducing

Setup instructions will be added after a clean-install test. This has not been done yet.

## License

MIT. See `LICENSE`.
