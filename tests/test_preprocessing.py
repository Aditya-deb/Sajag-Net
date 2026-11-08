import pytest
import pandas as pd
import sys, os
sys.path.append(os.path.abspath("src"))
from sajagnet.preprocessing import clean_column_names, deduplicate_data, map_labels

def test_column_cleaning_real():
    df = pd.DataFrame({' Flow Duration ': [1], 'B ': [2]})
    cleaned = clean_column_names(df)
    assert 'Flow Duration' in cleaned.columns
    assert ' Flow Duration ' not in cleaned.columns

def test_deduplicate_real():
    df = pd.DataFrame({'A': [1, 1, 2], 'B': [3, 3, 4]})
    deduped = deduplicate_data(df)
    assert len(deduped) == 2

def test_label_mapping_real():
    df = pd.DataFrame({'Label': ['BENIGN', 'DoS Hulk', 'FTP-Patator', 'Unknown']})
    mapped = map_labels(df)
    assert mapped['Label'].iloc[0] == 'Benign'
    assert mapped['Label'].iloc[1] == 'DoS/DDoS'
    assert mapped['Label'].iloc[2] == 'Brute Force'
    assert mapped['Label'].iloc[3] == 'Unknown'
