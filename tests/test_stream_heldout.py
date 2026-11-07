import sys, os
import pandas as pd
import joblib

def test_stream_is_held_out():
    stream_path = os.path.join("data", "sample_stream.csv")
    train_idx_path = os.path.join("models", "training_indices.pkl")
    
    # Check if stream exists
    assert os.path.exists(stream_path), "Sample stream missing!"
    
    # If we saved training indices during Phase 2, verify zero overlap
    if os.path.exists(train_idx_path):
        train_indices = joblib.load(train_idx_path)
        stream_df = pd.read_csv(stream_path)
        if 'source_index' in stream_df.columns:
            overlap = set(stream_df['source_index']).intersection(set(train_indices))
            assert len(overlap) == 0, f"Data leak detected! {len(overlap)} rows overlap with training data."
