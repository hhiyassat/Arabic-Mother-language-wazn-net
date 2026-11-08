#!/usr/bin/env python3
"""measure_classifier.py — القياس الآلي لمصنِّف نوع الجذر على أحداث HFN v36 المجرّدة (قراءة فقط).

لكل حدث ثلاثي مجرّد: يُصنَّف الجذر من لفظ الفعل، ويُصرَّف الماضي «هو» بالمحرك، ويُقارن بفعل HFN
(NFC، السكون اختياري، كرسي الهمزة موحَّد لأن HFN يكتبها على السطر أحياناً).
المخرَج: evidence/classifier_auto_v1.tsv وملخّص. يرفض الكتابة فوق ملف قائم.
"""
# v2 of the measurement (owner 2026-11-08 «اكمل باسلوب العلماء والمراجع»): the same comparison re-run on the newest HusseinFrameNet
# release (HFN_RELEASE to pin; MEASURE_OUT to write elsewhere). The v36 measurement and its judged sample stay as they were.
# Only change besides the release: HFN v44+ writes همزة الوصل «ٱ» (owner ruling 2026-11-07), so ٱ = ا when comparing.
import csv, os, sys, re, unicodedata, collections as C
import re
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, H)
from core.classify import classify, past_baab
from core.support import Unsupported, check_supported
from engines.morphological_engine import conjugate

def _newest_release():
    """HFN release to measure: HFN_RELEASE env (e.g. release_v36), else the newest release_vN with a MANIFEST."""
    base = os.path.expanduser("~/arabic-net/HusseinFrameNet/release/")
    pin = os.environ.get("HFN_RELEASE")
    if pin: return base + pin + "/"
    vs = [d for d in os.listdir(base) if re.fullmatch(r"release_v\d+", d) and os.path.exists(base + d + "/MANIFEST.json")]
    return base + max(vs, key=lambda d: int(d[9:])) + "/"
EV = _newest_release() + "events.csv"
OUT = os.environ.get("MEASURE_OUT") or os.path.join(H, "evidence", "classifier_auto_v4.tsv")   # v4: = v3 on the newest release
HU = ("غائب", "مفرد", "مذكر")


def norm(s):
    s = unicodedata.normalize("NFC", s).replace("ْ", "").replace("ٱ", "ا")
    for a in "أإؤئ":
        s = s.replace(a, "ء")
    return s


def main():
    if os.path.exists(OUT):
        sys.exit(OUT + " exists — not overwritten")
    rows, st = [], C.Counter()
    for e in csv.DictReader(open(EV, encoding="utf-8")):
        if e["layer"] not in ("الثلاثي", "المجرد"):
            continue
        r = dict(event_id=e["event_id"], root=e["root_K"], verb=e["verb"], form=e["form"], root_type="", code="", engine="", status="")
        try:
            k = classify(e["root_K"], e["verb"])
            r["root_type"] = k.root_type.value + ("+مهموز" if k.mahmuz else "")
            b = past_baab(e["form"])
            if b is None:
                r["status"] = "NO_BAAB"
            else:
                check_supported(e["root_K"].replace("أ", "ء"), k.root_type)
                got = conjugate(e["root_K"], k.root_type, b).table("ماضٍ", "معلوم")[HU]
                r["engine"] = got
                r["status"] = "MATCH" if norm(got) == norm(e["verb"]) else "MISMATCH"
        except Unsupported as x:
            r["code"], r["status"] = x.code, "REJECTED"
        st[(r["status"], r["root_type"] or r["code"])] += 1
        rows.append(r)
    with open(OUT, "w", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    tot = C.Counter(r["status"] for r in rows)
    print(len(rows), dict(tot))
    m, mm = tot["MATCH"], tot["MISMATCH"]
    print(f"match among compared: {m}/{m+mm} = {m/(m+mm):.3f}")
    for k, v in sorted(st.items(), key=lambda x: -x[1]):
        print(" ", k, v)


if __name__ == "__main__":
    main()
