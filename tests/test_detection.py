import pytest
import sys, os
import joblib
import pandas as pd
import json

@pytest.mark.skipif(not os.path.exists(os.path.join("models", "lgbm_model.pkl")), reason="Requires trained model")
def test_model_loads_and_predicts_known_classes():
    model = joblib.load(os.path.join("models", "lgbm_model.pkl"))
    le = joblib.load(os.path.join("models", "label_encoder.pkl"))
    
    # Assert model has predict method
    assert hasattr(model, 'predict')
    
    # Assert only the 5 known classes exist in the encoder
    known_classes = {'Benign', 'DoS/DDoS', 'PortScan', 'Brute Force', 'Web Attack'}
    encoder_classes = set(le.classes_)
    assert encoder_classes.issubset(known_classes), f"Found unexpected classes: {encoder_classes - known_classes}"

@pytest.mark.skipif(not os.path.exists(os.path.join("models", "lgbm_model.pkl")), reason="Requires trained model")
def test_model_consumes_exact_feature_columns():
    model = joblib.load(os.path.join("models", "lgbm_model.pkl"))
    with open("feature_columns.json", "r") as f:
        feature_cols = json.load(f)
        
    assert len(model.feature_name_) == len(feature_cols)
    assert set(model.feature_name_) == set(feature_cols)
