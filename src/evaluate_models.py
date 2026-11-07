import os, json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import lightgbm as lgb
from sklearn.metrics import confusion_matrix, f1_score, average_precision_score, accuracy_score, recall_score
from sklearn.preprocessing import LabelEncoder, label_binarize

df = pd.read_parquet("data/processed/cleaned_subset.parquet")
port_cols = [c for c in df.columns if "port" in c.lower()]
tcp_cols = ["Init_Win_bytes_forward", "Init_Win_bytes_backward", "min_seg_size_forward"]

X_no_ports = df.drop(columns=["Label"] + port_cols)
X_no_ports_no_tcp = df.drop(columns=["Label"] + port_cols + tcp_cols)
y = df["Label"]

encoder = LabelEncoder()
y_enc = encoder.fit_transform(y)

X_tr_np, X_te_np, y_tr, y_te = train_test_split(X_no_ports, y_enc, test_size=0.2, random_state=42, stratify=y_enc)
X_tr_npt, X_te_npt, _, _ = train_test_split(X_no_ports_no_tcp, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

def evaluate(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)
    
    cm = confusion_matrix(y_test, y_pred)
    benign_idx = list(encoder.classes_).index("Benign")
    actual_benign = cm[benign_idx, :].sum()
    false_alarms = actual_benign - cm[benign_idx, benign_idx]
    fpr = float(false_alarms / actual_benign) if actual_benign > 0 else 0.0
    
    mac_pr_auc = float(average_precision_score(label_binarize(y_test, classes=range(len(encoder.classes_))), y_prob, average="macro"))
    
    per_class_rec = recall_score(y_test, y_pred, average=None)
    recall_dict = {encoder.classes_[i]: float(per_class_rec[i]) for i in range(len(encoder.classes_))}
    
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "macro_f1": float(f1_score(y_test, y_pred, average="macro")),
        "macro_pr_auc": mac_pr_auc,
        "benign_fpr": fpr,
        "false_alarms_per_100k": fpr * 100000,
        "per_class_recall": recall_dict
    }

print("[*] Training 1: Decision Tree Baseline...")
dt = DecisionTreeClassifier(max_depth=8, random_state=42)
metrics_dt = evaluate(dt, X_tr_np, X_te_np, y_tr, y_te)

print("[*] Training 2: LightGBM (No Ports)...")
clf_np = lgb.LGBMClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1, verbose=-1)
metrics_np = evaluate(clf_np, X_tr_np, X_te_np, y_tr, y_te)

print("[*] Training 3: LightGBM (No Ports + No TCP Fingerprints)...")
clf_npt = lgb.LGBMClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1, verbose=-1)
metrics_npt = evaluate(clf_npt, X_tr_npt, X_te_npt, y_tr, y_te)

metrics = {
    "Decision_Tree_Baseline": metrics_dt,
    "LightGBM_No_Ports": metrics_np,
    "LightGBM_No_Ports_No_TCP": metrics_npt
}

os.makedirs("reports", exist_ok=True)
with open("reports/metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)
    
print("\n[+] Evaluation complete. Metrics saved.")
print("=== METRICS.JSON CONTENTS ===")
print(json.dumps(metrics, indent=4))
print("=============================")
