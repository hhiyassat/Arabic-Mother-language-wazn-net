#!/usr/bin/env python3
"""build_transitivity_wasit_v5.py — التعدّي في المجرّد: v1 مصحَّحاً بإحصاء قارئَين (المالك 2026-11-08: «اكمل باسلوب العلماء والمراجع»).

السبب: v2/v3 (ومنها نسخة v4 على HFN v45) غيّرت وسم 470 فعلاً مجرّداً عن v1، ولم تُقَس قواعدهما على المجرّد قطّ
(عيّنة v3 كانت للمزيد: 44/59 = 0.746 → BLOCK). فقُرئت الأفعال الـ470 كلّها (إحصاء لا عيّنة) بقارئَين أعمَيَين
لا يريان أيّ وسم، من أُطر الوسيط ونصّ مادّته (evidence/transitivity_census_v5/): TR_KEY.tsv والقراءات TR_[AB]_R[12].tsv.
الحدّ: «المتعدّي ما نصب مفعولاً به بنفسه، واللازم ما لم يتجاوز فاعله إلا بحرف جرّ» (سيبويه، الكتاب؛ شذا العرف).
النتيجة على 464 فعلاً اتّفق فيها القارئان: وسم v1 صحيح في 263، ووسم v3/v4 في 150، ولا هذا ولا ذاك في 51.
فلا يُنقل إلى v4، بل:
  اتّفق القارئان → وسمهما (basis CENSUS2_v5)، والحرف من قراءتهما إن اتّفقا عليه
  اختلفا (6)     → وسم v1 كما هو، basis CENSUS2_DISAGREE_KEEP_v1
  لم يُقرأ      → وسم v1 كما هو (مقيس 44/44 في v1)، basis V1
المدخل data/transitivity_wasit.tsv (v1، لا يُمسّ). المخرَج data/transitivity_wasit_v5.tsv (المجرّد وحده؛ المزيد بقي محجوباً).
CANDIDATE. يرفض الكتابة فوق ملف قائم."""
import csv, os, sys, collections as C
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V1, OUT, D = H + "/data/transitivity_wasit.tsv", H + "/data/transitivity_wasit_v5.tsv", H + "/evidence/transitivity_census_v5/"
if os.path.exists(OUT): sys.exit(OUT + " exists")
csv.field_size_limit(10 ** 8)
def t(n): return {r["tid"]: r for r in csv.DictReader(open(D + n, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)}
KEY = t("TR_KEY.tsv"); R1 = {**t("TR_A_R1.tsv"), **t("TR_B_R1.tsv")}; R2 = {**t("TR_A_R2.tsv"), **t("TR_B_R2.tsv")}
assert set(KEY) == set(R1) == set(R2), "census incomplete"
TAG = {"MUTAADI": "متعدي", "LAZIM": "لازم", "MUSHTARAK": "مشترك", "UNKNOWN": "غير معلوم"}
dec = {}
for k, r in KEY.items():
    a, b = R1[k], R2[k]
    if a["verdict"] == b["verdict"]:
        dec[r["event_id"]] = (TAG[a["verdict"]], a["harf"] if a["harf"].strip() == b["harf"].strip() else "", "CENSUS2_v5")
    else:
        dec[r["event_id"]] = (None, None, "CENSUS2_DISAGREE_KEEP_v1")
rows = list(csv.DictReader(open(V1, encoding="utf-8"), delimiter="\t"))
cols = list(rows[0]) + ["transitivity_v1", "harf_v1", "basis_v5"]
c = C.Counter()
for r in rows:
    r["transitivity_v1"], r["harf_v1"], r["basis_v5"] = r["transitivity_wasit"], r["harf"], "V1"
    d = dec.get(r["event_id"])
    if not d: continue
    tag, harf, basis = d; r["basis_v5"] = basis
    if tag is not None:
        r["transitivity_wasit"] = tag; r["harf"] = harf if tag == "لازم" else ""
    c[(r["transitivity_v1"], r["transitivity_wasit"], basis)] += 1
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)
print(len(rows), "rows; changed", sum(v for (a, b, _), v in c.items() if a != b), dict(c))
