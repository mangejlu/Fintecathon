import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONFIDENCE_LEVELS = {"high", "medium", "low"}


def load(name):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", sorted(DATA_DIR.glob("*.json")), ids=lambda p: p.name)
def test_data_file_is_valid_json(path):
    json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["rules.json", "payees.json"])
def test_every_row_carries_source_date_and_confidence(name):
    rows = load(name)
    assert rows, f"{name} is empty"
    for row in rows:
        assert row.get("source"), f"{row.get('id')} has no source"
        assert "date_checked" in row, f"{row.get('id')} has no date_checked"
        assert row.get("confidence") in CONFIDENCE_LEVELS, f"{row.get('id')} has a bad confidence"


def test_profile_carries_source_date_and_confidence():
    profile = load("profile.json")
    assert profile.get("source")
    assert "date_checked" in profile
    assert profile.get("confidence") in CONFIDENCE_LEVELS


def test_placeholder_rules_are_low_confidence_and_undated():
    for row in load("rules.json"):
        if row["source"] == "placeholder":
            assert row["confidence"] == "low"
            assert row["date_checked"] is None


def test_rules_cover_the_four_routes():
    ids = {row["id"] for row in load("rules.json")}
    assert ids == {"alipay_foreign_card", "wechat_foreign_card", "card_direct", "bank_transfer"}
