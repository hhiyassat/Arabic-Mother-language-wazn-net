#!/usr/bin/env python3
"""measure_rubai.py — مقابلة الرباعي (rubai_engine) بأحداث HFN v36 الرباعية: الماضي «هو» والمصدر. قراءة فقط.
التوحيد: NFC، السكون اختياري، همزة الوصل بلا حركة (HFN يكتب «ازْلَغَبَّ»، والمحرك «اِزْلَغَبَّ»: اصطلاح C3).
المخرَج evidence/rubai_vs_hfn_v1.tsv (يرفض الكتابة فوقه)."""
# v2 of the measurement (owner 2026-11-08 «اكمل باسلوب العلماء والمراجع»): the same comparison re-run on the newest HusseinFrameNet
# release (HFN_RELEASE to pin; MEASURE_OUT to write elsewhere). The v36 measurement and its judged sample stay as they were.
# Only change besides the release: HFN v44+ writes همزة الوصل «ٱ» (owner ruling 2026-11-07), so ٱ = ا when comparing.
import csv, os, sys, unicodedata, collections as C
import re
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, H)
from engines.rubai_engine import conjugate_rubai, derive_rubai, WAZN_BY_FORM
from core.support import Unsupported
def _newest_release():
    """HFN release to measure: HFN_RELEASE env (e.g. release_v36), else the newest release_vN with a MANIFEST."""
    base = os.path.expanduser("~/arabic-net/HusseinFrameNet/release/")
    pin = os.environ.get("HFN_RELEASE")
    if pin: return base + pin + "/"
    vs = [d for d in os.listdir(base) if re.fullmatch(r"release_v\d+", d) and os.path.exists(base + d + "/MANIFEST.json")]
    return base + max(vs, key=lambda d: int(d[9:])) + "/"
EV = _newest_release() + "events.csv"
OUT = os.environ.get("MEASURE_OUT") or os.path.join(H, "evidence", "rubai_vs_hfn_v2.tsv")
HU = ("غائب", "مفرد", "مذكر")
def n(s):
    s = unicodedata.normalize("NFC", s or "").replace("ْ", "").replace("ٱ", "ا").strip()
    return s[0] + s[2:] if s[:1] == "ا" and s[1:2] in "َُِ" else s
if os.path.exists(OUT): sys.exit(OUT + " exists")
rows, st = [], C.Counter()
for e in csv.DictReader(open(EV, encoding="utf-8")):
    w = WAZN_BY_FORM.get(e["form"].split(" ")[0])
    if not w: continue
    r = dict(event_id=e["event_id"], root=e["root_K"], form=e["form"], wazn=w, hfn_verb=e["verb"], hfn_masdar=e["masdar"],
             verb="", masdar="", verb_status="", masdar_status="")
    try:
        p = conjugate_rubai(e["root_K"], w); d = derive_rubai(e["root_K"], w)
        r["verb"] = p.table("ماضٍ", "معلوم")[HU]; r["masdar"] = d["masdar"]
        r["verb_status"] = "MATCH" if n(r["verb"]) == n(e["verb"]) else "DIFF"
        if not e["masdar"]: r["masdar_status"] = "HFN_EMPTY"
        else: r["masdar_status"] = "MATCH" if any(n(m) == n(e["masdar"]) for m in d["masdar"].split("/")) else "DIFF"
    except Unsupported as x:
        r["verb_status"] = r["masdar_status"] = "REJECTED:" + x.code
    st[(w, "verb", r["verb_status"])] += 1; st[(w, "masdar", r["masdar_status"])] += 1
    rows.append(r)
with open(OUT, "w", encoding="utf-8") as f:
    wr = csv.DictWriter(f, list(rows[0]), delimiter="\t", lineterminator="\n"); wr.writeheader(); wr.writerows(rows)
print(len(rows))
for k, v in sorted(st.items()): print(" ", k, v)
for r in rows:
    if "DIFF" in (r["verb_status"], r["masdar_status"]): print(" DIFF", r["root"], r["wazn"], r["hfn_verb"], r["verb"], "|", r["hfn_masdar"], r["masdar"])
