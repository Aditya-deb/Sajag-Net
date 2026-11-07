import os
import glob
import numpy as np
import pandas as pd

RAW_DATA_DIR = os.path.join("data", "raw")
OUTPUT_PATH = os.path.join("data", "processed", "cleaned_subset.parquet")

LABEL_MAPPING = {
    "Normal Traffic": "Benign", "BENIGN": "Benign", "Benign": "Benign",
    "DoS": "DoS/DDoS", "DDoS": "DoS/DDoS", "DoS Hulk": "DoS/DDoS", 
    "DoS GoldenEye": "DoS/DDoS", "DoS slowloris": "DoS/DDoS", "DoS Slowhttptest": "DoS/DDoS",
    "Port Scanning": "PortScan", "PortScan": "PortScan",
    "Brute Force": "Brute Force", "FTP-Patator": "Brute Force", "SSH-Patator": "Brute Force",
    "Web Attacks": "Web Attack", "Web Attack": "Web Attack", "Web Attack  Brute Force": "Web Attack", 
    "Web Attack  XSS": "Web Attack", "Web Attack  Sql Injection": "Web Attack"
}

def clean_and_sample():
    csv_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.csv"))
    if not csv_files:
        print("[!] No CSV found in data/raw!")
        return

    file_path = csv_files[0]
    print(f"[*] Processing {os.path.basename(file_path)}...")

    dfs = []
    for chunk in pd.read_csv(file_path, chunksize=50000, low_memory=False):
        chunk.columns = chunk.columns.str.strip().str.replace(" ", "_")
        
        label_col = "Attack_Type" if "Attack_Type" in chunk.columns else "Label"
        if label_col not in chunk.columns:
            continue
            
        chunk["Label"] = chunk[label_col].astype(str).str.strip().map(LABEL_MAPPING)
        chunk = chunk.dropna(subset=["Label"])
        if chunk.empty:
            continue

        if "Attack_Type" in chunk.columns and label_col == "Attack_Type":
            chunk.drop(columns=["Attack_Type"], inplace=True)

        for col_to_drop in ["Flow_ID", "Source_IP", "Destination_IP", "Timestamp", "SimillarHTTP"]:
            if col_to_drop in chunk.columns:
                chunk.drop(columns=[col_to_drop], inplace=True)

        chunk.replace([np.inf, -np.inf], np.nan, inplace=True)
        chunk.dropna(inplace=True)

        float_cols = chunk.select_dtypes(include=["float64"]).columns
        chunk[float_cols] = chunk[float_cols].astype("float32")
        int_cols = chunk.select_dtypes(include=["int64"]).columns
        chunk[int_cols] = chunk[int_cols].astype("int32")

        dfs.append(chunk)

    full_df = pd.concat(dfs, ignore_index=True)
    
    print(f"[*] Rows before deduplication: {len(full_df)}")
    full_df.drop_duplicates(inplace=True)
    print(f"[*] Rows after deduplication: {len(full_df)}")

    target_caps = {
        "Benign": 100000,
        "DoS/DDoS": 30000,
        "PortScan": 10000,
        "Brute Force": 5000,
        "Web Attack": 3000
    }

    sampled_dfs = []
    for label, cap in target_caps.items():
        subset = full_df[full_df["Label"] == label]
        n_samples = min(len(subset), cap)
        if n_samples > 0:
            sampled_dfs.append(subset.sample(n=n_samples, random_state=42))

    final_df = pd.concat(sampled_dfs, ignore_index=True).sample(frac=1.0, random_state=42).reset_index(drop=True)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    final_df.to_parquet(OUTPUT_PATH, index=False)
    print(f"[+] Saved {len(final_df)} highly-cleaned rows to {OUTPUT_PATH}")

if __name__ == "__main__":
    clean_and_sample()
