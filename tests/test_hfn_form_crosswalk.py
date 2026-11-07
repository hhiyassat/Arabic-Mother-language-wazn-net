"""كلّ اسم بناء في HFN له وزن في wazn-net، والمحرّك يبني فعل الحدث نفسه للمزيدات (data/hfn_form_crosswalk.tsv)."""
import csv
import os
import re

import pytest

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NET = os.environ.get("ARABIC_NET_HOME", os.path.dirname(W))
XW = os.path.join(W, "data", "hfn_form_crosswalk.tsv")
RELS = os.path.join(NET, "HusseinFrameNet", "release")
pytestmark = pytest.mark.skipif(not os.path.isdir(RELS), reason="HusseinFrameNet غير موجود")


def _newest():
    return max((d for d in os.listdir(RELS) if re.fullmatch(r"release_v\d+", d)), key=lambda d: int(d[9:]))


def test_every_hfn_form_is_mapped():
    rows = {r["hfn_form"]: r for r in csv.DictReader(open(XW, encoding="utf-8"), delimiter="\t")}
    ev = csv.DictReader(open(os.path.join(RELS, _newest(), "events.csv"), encoding="utf-8"))
    forms = {e["form"] for e in ev if not e["event_review_v36"].startswith("WITHDRAWN")}
    assert forms <= set(rows), sorted(forms - set(rows))
    assert all(rows[f]["status"] == "MAPPED" and rows[f]["wazn_ids"] for f in forms)


def test_engine_agrees_with_hfn_for_derived_forms():
    rows = list(csv.DictReader(open(XW, encoding="utf-8"), delimiter="\t"))
    assert sum(int(r["engine_match"]) for r in rows) > 6000
    assert sum(int(r["engine_mismatch"]) for r in rows) == 0
