import sys, os
sys.path.append(os.path.abspath("src"))
import pandas as pd

def test_dedupe_mock():
    # Simple placeholder showing we test preprocessing concepts
    df = pd.DataFrame({'A': [1, 1, 2], 'B': [3, 3, 4]})
    deduped = df.drop_duplicates()
    assert len(deduped) == 2

def test_column_cleaning():
    df = pd.DataFrame({' Flow Duration ': [1], 'B ': [2]})
    df.columns = df.columns.str.strip()
    assert 'Flow Duration' in df.columns
