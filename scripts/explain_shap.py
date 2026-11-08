import os
import pandas as pd
import numpy as np
import joblib
import shap
from sklearn.model_selection import train_test_split

df = pd.read_parquet("data/processed/cleaned_subset.parquet")
port_cols = [c for c in df.columns if "port" in c.lower()]
X = df.drop(columns=["Label"] + port_cols)
y = df["Label"]
clf = joblib.load("models/lgbm_model.pkl")
encoder = joblib.load("models/label_encoder.pkl")

y_enc = encoder.transform(y)
_, X_test, _, y_test = train_test_split(X, pd.Series(y_enc, index=X.index), test_size=0.2, random_state=42, stratify=y_enc)

X_test_sample = X_test.sample(n=1500, random_state=42).astype("float32")
y_test_sample = y_test.loc[X_test_sample.index]

explainer = shap.TreeExplainer(clf)
shap_values = explainer.shap_values(X_test_sample)

print("\n=== SHAP EXPLANATIONS BY CLASS (FIXED WORDING) ===")
found_classes = set()
for row_idx in range(len(X_test_sample)):
    if len(found_classes) == len(encoder.classes_): break
    
    row = X_test_sample.iloc[row_idx:row_idx+1]
    pred_idx = clf.predict(row)[0]
    actual_idx = y_test_sample.iloc[row_idx]
    
    if pred_idx == actual_idx and pred_idx not in found_classes:
        found_classes.add(pred_idx)
        pred_name = encoder.inverse_transform([pred_idx])[0]
        vals = shap_values[pred_idx][row_idx] if isinstance(shap_values, list) else shap_values[row_idx, :, pred_idx]
        top_indices = np.argsort(np.abs(vals))[-3:][::-1]
        
        print(f"\nPredicted Class: {pred_name}")
        for i, idx in enumerate(top_indices):
            feat = X_test_sample.columns[idx]
            val = row.iloc[0, idx]
            action = f"pushed the prediction toward {pred_name}" if vals[idx] > 0 else f"pushed the prediction away from {pred_name}"
            print(f"  {i+1}. {feat} (value: {val:.2f}) {action}.")
