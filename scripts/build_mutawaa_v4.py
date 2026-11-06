#!/usr/bin/env python3
"""build_mutawaa_v4.py — data/mutawaa_v4.tsv = mutawaa_v3.tsv وتشكيلُ المطاوع/الأصل من حدث HFN الذي يربطه الصفّ نفسه.

العيب في v3 (فحص الجذور، الدفعة 1، 2026-11-06): صفوف R1W_WASIT أخذت تشكيل المطاوع من نصّ الوسيط (OCR):
«انقلب» بلا حركات، «اجْتمَعَ» تاؤه بلا حركة، «تَطَهِرَ» و«تَسَلَفَ» بلا شدّة وزنهما تَفَعَّلَ، «انْدَرَّس».
والصفّ نفسه يسمّي حدث HFN (mutawaa_event / base_event) المشكولَ تشكيلاً تامّاً.

القاعدة: إذا كان للصفّ حدثٌ في HFN، وحروفُه (بلا حركات) هي حروف الصفّ، وخالفه التشكيل → يؤخذ تشكيل HFN،
ويُحفظ الأصل في mutawaa_v3_text / base_v3_text، ويُعلَّم vowel_src=HFN:<event_id>.
إن اختلفت الحروف لا يُمسّ الصفّ (يُعدّ ويُطبع). v1 وv2 وv3 لا تُمسّ.

الدمج: صفّ R1W_WASIT الذي يصير بعد التصحيح الزوجَ نفسه (base, mutawaa) لصفٍّ سابق — وكان v3 يُبقيه لأنّ
تشكيل الوسيط أخفى التكرار — يُدمج في الصفّ السابق على عُرف الجدول («R1_QABILIYYAT+LEX_FORMULA»):
route += «+R1W_WASIT»، وbase_event/mutawaa_event يُملآن منه إن كانا فارغين، وmerged_v3_line يحفظ سطره في v3.
"""
import csv, os, re, sys, unicodedata
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V3, OUT = H + "/data/mutawaa_v3.tsv", H + "/data/mutawaa_v4.tsv"
HFN = os.path.expanduser(os.environ.get("HFN_EVENTS",
      "~/arabic-net/HusseinFrameNet/release/release_v37/events.csv"))
HAR = re.compile("[ً-ْٰ]")
if os.path.exists(OUT): sys.exit(OUT + " exists")


def nfc(s): return unicodedata.normalize("NFC", (s or "").strip())
def letters(s): return HAR.sub("", nfc(s))


ev = {e["event_id"]: nfc(e["verb"]) for e in csv.DictReader(open(HFN, encoding="utf-8"))}
rows = list(csv.DictReader(open(V3, encoding="utf-8"), delimiter="\t"))
cols = list(rows[0]) + ["mutawaa_v3_text", "base_v3_text", "vowel_src", "merged_v3_line"]
fixed = {"mutawaa": 0, "base": 0}; skipped = []
for r in rows:
    r["mutawaa_v3_text"] = r["base_v3_text"] = ""; src = []
    for side, eid, keep in (("mutawaa", "mutawaa_event", "mutawaa_v3_text"), ("base", "base_event", "base_v3_text")):
        h = ev.get(r[eid])
        if not h or nfc(r[side]) == h:
            continue
        if letters(r[side]) != letters(h):
            skipped.append((r["root"], side, r[side], h)); continue
        r[keep], r[side] = r[side], h
        src.append(f"{side}=HFN:{r[eid]}"); fixed[side] += 1
    r["vowel_src"] = " · ".join(src)
    r["merged_v3_line"] = ""
out, seen, merged = [], {}, []
for i, r in enumerate(rows):
    k = (r["base"], r["mutawaa"])
    if k in seen and r["route"] == "R1W_WASIT":
        a = seen[k]
        a["route"] += "+R1W_WASIT"
        for e in ("base_event", "mutawaa_event"):
            if not a[e]: a[e] = r[e]
        a["merged_v3_line"] = (a["merged_v3_line"] + " " if a["merged_v3_line"] else "") + str(i + 2)
        merged.append((k, i + 2)); continue
    seen.setdefault(k, r); out.append(r)
rows = out
with open(OUT, "w", encoding="utf-8") as f:
    w = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)
print(len(rows), "rows; vowelling from HFN:", fixed, "merged:", len(merged), "letters differ (untouched):", len(skipped), "->", OUT)
for s in skipped: print("  SKIP", s)
