import pandas as pd
import numpy as np

def clean_column_names(df):
    df.columns = df.columns.str.strip()
    return df

def deduplicate_data(df):
    return df.drop_duplicates()

def map_labels(df, label_col='Label'):
    if label_col in df.columns:
        # Example mapping based on your previous scripts
        df[label_col] = df[label_col].replace({
            'BENIGN': 'Benign',
            'DoS Hulk': 'DoS/DDoS',
            'DoS GoldenEye': 'DoS/DDoS',
            'DoS slowloris': 'DoS/DDoS',
            'DoS Slowhttptest': 'DoS/DDoS',
            'DDoS': 'DoS/DDoS',
            'FTP-Patator': 'Brute Force',
            'SSH-Patator': 'Brute Force',
            'Web Attack  Brute Force': 'Web Attack',
            'Web Attack  XSS': 'Web Attack',
            'Web Attack  Sql Injection': 'Web Attack'
        })
    return df
