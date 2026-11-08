import sys, os
import pandas as pd
import numpy as np

def test_stream_is_held_out():
    stream_path = os.path.join("data", "sample_stream.csv")
    train_idx_path = os.path.join("data", "train_indices.npy")
    assert os.path.exists(stream_path), "Sample stream missing!"
    assert os.path.exists(train_idx_path), "Training indices missing!"
    
    train_indices = np.load(train_idx_path, allow_pickle=True)
    stream_df = pd.read_csv(stream_path)
    
    if 'source_index' in stream_df.columns:
        overlap = set(stream_df['source_index']).intersection(set(train_indices))
        assert len(overlap) == 0, f"Data leak detected! {len(overlap)} rows overlap."
