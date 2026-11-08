import os
import pandas as pd
import lightgbm as lgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DATA_PATH = os.path.join("data", "processed", "cleaned_subset.parquet")
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "lgbm_model.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

df = pd.read_parquet(DATA_PATH)
port_cols = [c for c in df.columns if "port" in c.lower()]
X = df.drop(columns=["Label"] + port_cols)
y = df["Label"]

encoder = LabelEncoder()
y_enc = encoder.fit_transform(y)
X_tr, X_te, y_tr, y_te = train_test_split(X, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

print("[*] Retraining LightGBM without Port features...")
clf = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.1, class_weight='balanced', random_state=42, n_jobs=-1, verbose=-1)
clf.fit(X_tr, y_tr)

os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(clf, MODEL_PATH)
joblib.dump(encoder, ENCODER_PATH)
print("[+] No-Port Model saved successfully.")

# Saved training indices to data/train_indices.npy
