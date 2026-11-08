#!/usr/bin/env python3
"""measure_mahmuz.py — مقابلة اسمَي الفاعل والمفعول للمهموز السالم (derive_names) بمداخل HFN v36 (lexical_units: اسم فاعل/اسم مفعول).
المقارنة مرّتين: بعد توحيد كرسي الهمزة (لأن HFN يكتبها على السطر أحياناً)، وحرفاً بحرف (الرسم). قراءة فقط.
المخرَج: evidence/mahmuz_vs_hfn_v1.tsv (يرفض الكتابة فوقه)."""
# v2 of the measurement (owner 2026-11-08 «اكمل باسلوب العلماء والمراجع»): the same comparison re-run on the newest HusseinFrameNet
# release (HFN_RELEASE to pin; MEASURE_OUT to write elsewhere). The v36 measurement and its judged sample stay as they were.
# Only change besides the release: HFN v44+ writes همزة الوصل «ٱ» (owner ruling 2026-11-07), so ٱ = ا when comparing.
import csv, os, sys, unicodedata, collections as C
import re
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, H)
from core.classify import classify
from core.support import Unsupported
from core.types import RootType
from engines.names_engine import derive_names
def _newest_release():
    """HFN release to measure: HFN_RELEASE env (e.g. release_v36), else the newest release_vN with a MANIFEST."""
    base = os.path.expanduser("~/arabic-net/HusseinFrameNet/release/")
    pin = os.environ.get("HFN_RELEASE")
    if pin: return base + pin + "/"
    vs = [d for d in os.listdir(base) if re.fullmatch(r"release_v\d+", d) and os.path.exists(base + d + "/MANIFEST.json")]
    return base + max(vs, key=lambda d: int(d[9:])) + "/"
REL = _newest_release()
OUT = os.environ.get("MEASURE_OUT") or os.path.join(H, "evidence", "mahmuz_vs_hfn_v2.tsv")
def n0(s): return unicodedata.normalize("NFC", s).replace("ٱ", "ا").replace("ْ", "").replace("ٌ", "").replace("ٍ", "").strip()
def seat(s):
    s = n0(s)
    for a in "أإؤئ": s = s.replace(a, "ء")
    return s.replace("آ", "ءا")
if os.path.exists(OUT): sys.exit(OUT + " exists")
E = {e["event_id"]: e for e in csv.DictReader(open(REL + "events.csv", encoding="utf-8")) if e["layer"] in ("الثلاثي", "المجرد")}
rows, st = [], C.Counter()
for lu in csv.DictReader(open(REL + "lexical_units.csv", encoding="utf-8")):
    if lu["pos_ar"] not in ("اسم فاعل", "اسم مفعول") or lu["event_id"] not in E: continue
    e = E[lu["event_id"]]
    try:
        k = classify(e["root_K"], e["verb"])
    except Unsupported:
        continue
    if not k.mahmuz: continue
    n = derive_names(e["root_K"], RootType.SAHIH, "I", "متعدي")
    got = n.ism_faail if lu["pos_ar"] == "اسم فاعل" else n.ism_mafuul
    alts = [got] + (["مَ" + got[2:].replace("ؤ", "ئ")] if "ؤ" in got else [])
    same_seat = any(seat(a) == seat(lu["lemma"]) for a in alts)
    exact = any(n0(a) == n0(lu["lemma"]) for a in alts)
    s = "EXACT" if exact else ("RASM_ONLY" if same_seat else "DIFF")
    st[(lu["pos_ar"], s)] += 1
    rows.append(dict(event_id=e["event_id"], root=e["root_K"], verb=e["verb"], pos=lu["pos_ar"], hfn=lu["lemma"], engine=got, status=s, basis=lu["basis"]))
with open(OUT, "w", encoding="utf-8") as f:
    w = csv.DictWriter(f, list(rows[0]), delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)
print(len(rows), dict(st))
for r in rows:
    if r["status"] == "DIFF": print(" DIFF", r["root"], r["verb"], r["pos"], r["hfn"], "←→", r["engine"])
