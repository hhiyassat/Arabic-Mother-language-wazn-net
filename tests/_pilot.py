"""_pilot.py — تحميل data/pilot_roots.json (بيانات المالك، commit 5a0536e)."""
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

PILOT_PATH = os.path.join(REPO, "data", "pilot_roots.json")


def _load():
    with open(PILOT_PATH, encoding="utf-8") as f:
        return json.load(f)


PILOT = _load()
PILOT_ROOTS = PILOT["roots"]
PILOT_BY_LETTERS = {r["letters"]: r for r in PILOT_ROOTS}


