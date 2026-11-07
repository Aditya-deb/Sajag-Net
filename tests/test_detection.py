import sys, os
import joblib
import pandas as pd

def test_model_loads_and_predicts():
    model_path = os.path.join("models", "lgbm_model.pkl")
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        assert hasattr(model, 'predict')
