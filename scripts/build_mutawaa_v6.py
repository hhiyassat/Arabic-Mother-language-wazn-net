#!/usr/bin/env python3
"""build_mutawaa_v6.py — data/mutawaa_v6.tsv = mutawaa_v5.tsv وحدثُ HFN للمطاوع في أزواج تَفَعْلَلَ السبعة (المالك 2026-11-08: «اعمل كل هذا بنفس شروطي»).

في v5 كان المطاوع في الأزواج السبعة (تَبَلْبَلَ…) بلا حدث في HFN، فتشكيله من نصّ الوسيط (OCR: «تبَلْبَلَ»، «تَدخْدَخَ»).
HFN release_v46 (HFN-D073) أضاف الأحداث السبعة بعد قراءة قارئين أعميين لشواهدها في المعاجم. فهنا، على قاعدة v4 نفسها:
صفّ v5 بلا mutawaa_event، وفي HFN حدثٌ على تَفَعْلَلَ من الجذر نفسه حروفُه حروفُ المطاوع → يُملأ mutawaa_event ويؤخذ تشكيل HFN،
ويُحفظ نصّ v5 في mutawaa_v5_text، وvowel_src += mutawaa=HFN:<event_id>. لا يُمسّ غير ذلك. v5 لا يُمسّ. يرفض الكتابة فوق ملف قائم."""
import csv, os, re, sys, unicodedata
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V5, OUT = H + "/data/mutawaa_v5.tsv", H + "/data/mutawaa_v6.tsv"
if os.path.exists(OUT): sys.exit(OUT + " exists")
REL = os.path.expanduser("~/arabic-net/HusseinFrameNet/release/")
REL += os.environ.get("HFN_RELEASE") or max((d for d in os.listdir(REL) if re.fullmatch(r"release_v\d+", d) and os.path.exists(REL + d + "/MANIFEST.json")), key=lambda d: int(d[9:]))
HAR = re.compile("[ً-ْٰ]")
def letters(s): return HAR.sub("", unicodedata.normalize("NFC", s or "")).replace("ٱ", "ا").strip()
EV = [e for e in csv.DictReader(open(REL + "/events.csv", encoding="utf-8")) if e["form"] == "تَفَعْلَلَ" and not e["event_review_v36"].startswith("WITHDRAWN")]
by = {(e["root_K"], letters(e["verb"])): e for e in EV}
rows = list(csv.DictReader(open(V5, encoding="utf-8"), delimiter="\t"))
cols = list(rows[0]) + ["mutawaa_v5_text"]
n = 0
for r in rows:
    r["mutawaa_v5_text"] = ""
    if r["mutawaa_event"]: continue
    e = by.get((r["root"], letters(r["mutawaa"])))
    if not e: continue
    r["mutawaa_v5_text"], r["mutawaa"], r["mutawaa_event"] = r["mutawaa"], e["verb"], e["event_id"]
    r["mutawaa_form"] = e["form"]
    if not r["athar"]: r["athar"], r["athar_src"] = e["masdar"], "HFN_MASDAR"
    r["vowel_src"] = "·".join(x for x in (r["vowel_src"], "mutawaa=HFN:" + e["event_id"]) if x); n += 1
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)
print(os.path.basename(REL), len(rows), "rows; linked", n, "→", OUT)
