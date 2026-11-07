# SajagNet Decisions Log
- **Split Strategy:** Random stratified split on deduplicated data. Chronological split was not possible because the Timestamp column was dropped to mitigate time-based dataset quirks.
- **Duplication:** Exact duplicates were removed prior to splitting.
- **Feature Selection (Ablation 1):** Port columns removed from model training to prevent reliance on dataset-specific port mappings. Retained for Phase 4 asset registry.
- **Feature Selection (Ablation 2):** OS/TCP-stack fingerprint columns (Init_Win_bytes_forward, Init_Win_bytes_backward, min_seg_size_forward) were evaluated for removal to ensure the model does not over-rely on lab-specific TCP generation quirks.

- **Model Selection (Phase 4):** Carry LightGBM_No_Ports forward as the PRIMARY model. Keep LightGBM_No_Ports_No_TCP as a robustness comparison.
- **Model Comparison:** Without TCP window features, false alarms rise from 130 to 2,365 per 100,000 benign flows, so performance depends substantially on them; they may partly reflect the lab setup. Also state that the Decision Tree baseline already reaches 99.11% accuracy, so the dataset is relatively easy.
