#!/usr/bin/env python3
"""build_mutawaa_v7.py — data/mutawaa_v7.tsv = mutawaa_v6.tsv + أحداث HFN v47 لأزواج تَفَعْلَلَ الخمسة الأقدم، وتصحيح «تمخلَّف»
(المالك 2026-11-08: «هذه ستّة صفوف تفعلل أقدم في جدول المطاوعة ليس لها حدث في HFN، و«تمخلّف» منها موضعه في الجدول خطأ»).

(١) تَبَرْقَعَ، تَجَرْجَمَ، تَدَهْدَمَ، تَدَهْدَهَ، تَكَعْبَرَ: أحداث في HFN release_v47 (HFN-D075) بعد قراءة قارئين لشواهدها؛ تُربط بقاعدة v6 نفسها.
(٢) صفّ خلف «تمخلَّفَ» (R1W_WASIT، الوسيط: «(تمخلَّفَ): مطاوع خَلَّفه»): الميم زيادة OCR (ومثلها «تَمخالَفا» في السطر نفسه)، وقرأه
    قارئان أعميان «تَخَلَّفَ» على تَفَعَّلَ مطاوعاً لخَلَّفَ (HFN/06_handoff/tafallala_v47/Q2B_R*.tsv، خلف#X). فيُصحَّح: المطاوع تَخَلَّفَ
    (HFN-E-228c4028fa، تَفَعَّلَ)، والأصل خَلَّفَ (HFN-E-23c44141b4، فَعَّلَ)، ويُحفظ النصّ القديم في mutawaa_v5_text وbase_status_v6.
    والزوج لم يكن في v6 بغير هذا الصفّ.
v6 لا يُمسّ. يرفض الكتابة فوق ملف قائم.
---- build_mutawaa_v6 ----
build_mutawaa_v6.py — data/mutawaa_v6.tsv = mutawaa_v5.tsv وحدثُ HFN للمطاوع في أزواج تَفَعْلَلَ السبعة (المالك 2026-11-08: «اعمل كل هذا بنفس شروطي»).

في v5 كان المطاوع في الأزواج السبعة (تَبَلْبَلَ…) بلا حدث في HFN، فتشكيله من نصّ الوسيط (OCR: «تبَلْبَلَ»، «تَدخْدَخَ»).
HFN release_v46 (HFN-D073) أضاف الأحداث السبعة بعد قراءة قارئين أعميين لشواهدها في المعاجم. فهنا، على قاعدة v4 نفسها:
صفّ v5 بلا mutawaa_event، وفي HFN حدثٌ على تَفَعْلَلَ من الجذر نفسه حروفُه حروفُ المطاوع → يُملأ mutawaa_event ويؤخذ تشكيل HFN،
ويُحفظ نصّ v5 في mutawaa_v5_text، وvowel_src += mutawaa=HFN:<event_id>. لا يُمسّ غير ذلك. v5 لا يُمسّ. يرفض الكتابة فوق ملف قائم."""
import csv, os, re, sys, unicodedata
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V5, OUT = H + "/data/mutawaa_v6.tsv", H + "/data/mutawaa_v7.tsv"
if os.path.exists(OUT): sys.exit(OUT + " exists")
REL = os.path.expanduser("~/arabic-net/HusseinFrameNet/release/")
REL += os.environ.get("HFN_RELEASE") or max((d for d in os.listdir(REL) if re.fullmatch(r"release_v\d+", d) and os.path.exists(REL + d + "/MANIFEST.json")), key=lambda d: int(d[9:]))
HAR = re.compile("[ً-ْٰ]")
def letters(s): return HAR.sub("", unicodedata.normalize("NFC", s or "")).replace("ٱ", "ا").strip()
EV = [e for e in csv.DictReader(open(REL + "/events.csv", encoding="utf-8")) if e["form"] == "تَفَعْلَلَ" and not e["event_review_v36"].startswith("WITHDRAWN")]
by = {(e["root_K"], letters(e["verb"])): e for e in EV}
rows = list(csv.DictReader(open(V5, encoding="utf-8"), delimiter="\t"))
cols = list(rows[0]) + (["mutawaa_v5_text"] if "mutawaa_v5_text" not in rows[0] else []) + ["base_status_v6"]
n = 0
for r in rows:
    r.setdefault("mutawaa_v5_text", ""); r["base_status_v6"] = ""
    if r["root"] == "خلف" and letters(r["mutawaa"]) == "تمخلف":
        ev = {e["event_id"]: e for e in csv.DictReader(open(REL + "/events.csv", encoding="utf-8"))}
        m, b = ev["HFN-E-228c4028fa"], ev["HFN-E-23c44141b4"]
        assert m["verb"] == "تَخَلَّفَ" and b["verb"] == "خَلَّفَ"
        r["mutawaa_v5_text"], r["base_status_v6"] = r["mutawaa"], r["base_status"]
        r.update(mutawaa=m["verb"], mutawaa_form=m["form"], mutawaa_event=m["event_id"], base=b["verb"], base_form=b["form"],
                 base_event=b["event_id"], base_status="OK", athar=m["masdar"], athar_src="HFN_MASDAR",
                 vowel_src="·".join(x for x in (r["vowel_src"], "CORRECTED_v7: OCR تمخلَّف = تَخَلَّفَ (قارئان)") if x)); n += 1
        continue
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
