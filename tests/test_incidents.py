import pytest
import pandas as pd
import sys, os
sys.path.append(os.path.abspath("src"))
from sajagnet.incidents import build_incidents

def test_incident_grouping_portscan():
    data = {'Predicted_Class': ['PortScan']*59, 'Destination_Port': list(range(1000, 1059)), 'Confidence': [0.99]*59}
    df = pd.DataFrame(data)
    inc_df = build_incidents(df)
    assert len(inc_df) == 1
    assert inc_df.iloc[0]['Flow Count'] == 59

def test_incident_grouping_dos():
    data = {'Predicted_Class': ['DoS/DDoS']*210, 'Destination_Port': [80]*210, 'Confidence': [0.99]*210}
    df = pd.DataFrame(data)
    inc_df = build_incidents(df)
    assert len(inc_df) == 1
    assert inc_df.iloc[0]['Flow Count'] == 210
