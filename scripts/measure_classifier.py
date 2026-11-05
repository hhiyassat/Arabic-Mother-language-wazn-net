#!/usr/bin/env python3
"""measure_classifier.py — القياس الآلي لمصنِّف نوع الجذر على أحداث HFN v36 المجرّدة (قراءة فقط).

لكل حدث ثلاثي مجرّد: يُصنَّف الجذر من لفظ الفعل، ويُصرَّف الماضي «هو» بالمحرك، ويُقارن بفعل HFN
(NFC، السكون اختياري، كرسي الهمزة موحَّد لأن HFN يكتبها على السطر أحياناً).
المخرَج: evidence/classifier_auto_v1.tsv وملخّص. يرفض الكتابة فوق ملف قائم.
"""
import csv, os, sys, re, unicodedata, collections as C
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, H)
from core.classify import classify, past_baab
from core.support import Unsupported, check_supported
from engines.morphological_engine import conjugate

EV = os.path.expanduser("~/arabic-net/HusseinFrameNet/release/release_v36/events.csv")
OUT = os.path.join(H, "evidence", "classifier_auto_v2.tsv")   # v2: قاعدة فَعُلَ الواوي
HU = ("غائب", "مفرد", "مذكر")


def norm(s):
    s = unicodedata.normalize("NFC", s).replace("ْ", "")
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
