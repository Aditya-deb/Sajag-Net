import json
from pathlib import Path

from sajagnet.config import THREAT_SEVERITY
from sajagnet.mitre_mapper import get_mitre_info
from sajagnet.risk_engine import ASSET_REGISTRY


def test_severity_comes_from_config():
    for cls, sev in THREAT_SEVERITY.items():
        assert get_mitre_info(cls)["severity"] == sev


def test_unknown_class_is_marked_unmapped():
    info = get_mitre_info("Mystery Attack")
    assert info["id"] == "UNMAPPED"
    assert info["id"] != "T1078"


def test_asset_registry_loaded_from_json():
    path = Path(__file__).resolve().parents[1] / "data" / "asset_registry.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    assert data == ASSET_REGISTRY
