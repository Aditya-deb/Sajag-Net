import pytest
import sys, os
sys.path.append(os.path.abspath("src"))
from sajagnet.mitre_mapper import get_mitre_info

@pytest.mark.parametrize("threat, expected_id", [
    ("Brute Force", "T1110"),
    ("Web Attack", "T1190"),
    ("DoS/DDoS", "T1498"),
    ("PortScan", "T1046")
])
def test_mitre_ids(threat, expected_id):
    assert get_mitre_info(threat)["id"] == expected_id
