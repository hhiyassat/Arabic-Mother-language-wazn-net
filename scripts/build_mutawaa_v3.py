#!/usr/bin/env python3
"""build_mutawaa_v3.py — يضيف إلى data/mutawaa.tsv مسلك R1W_WASIT من ahdath R1W v2 ويكتب data/mutawaa_v3.tsv
(v1 وv2 لا يُمسّان).

R1W v2: ~/arabic-net/Arabic-Mother-language-net/ahdath/mutawaa_R1W_pool.tsv — 140 زوجاً من نصّ الوسيط «X: مطاوع Yه»،
وصيغة الأصل فيها من شكل النصّ نفسه (دفَّقه ← فَعَّلَ)، وما سمّى النصّ له صيغةً ليست في HFN أُسقط.
مقيس في ahdath: 53/57 = 0.930، ويلسون الأدنى 0.833 → ACCEPT (قراءة فقط).
عيب v1 (إبدال الأصل بالمجرّد حين يغيب فَعَّلَ) أُصلح في المصدر؛ ويبقى هنا شرط الوزن احتياطاً: يُقبل الأصل
إذا وافق وزنُه وزنَ المطاوع وحده:
  تَفَعَّلَ ← فَعَّلَ · تَفَاعَلَ ← فَاعَلَ · تَفَعْلَلَ ← فَعْلَلَ · انْفَعَلَ/افْتَعَلَ ← فَعَلَ/فَعِلَ/فَعُلَ/أَفْعَلَ · المجرّد ← أَفْعَلَ/فَعَّلَ
وإلا يبقى المطاوع بنصّ أصله من الوسيط (base_text) والأصلُ فارغ: base_status=BASE_UNRESOLVED.
"""
import csv, os, re, sys, unicodedata
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V1, OUT = H + "/data/mutawaa.tsv", H + "/data/mutawaa_v3.tsv"
POOL = os.path.expanduser("~/arabic-net/Arabic-Mother-language-net/ahdath/mutawaa_R1W_pool.tsv")
HAR = re.compile("[ً-ْٰـ]")
if os.path.exists(OUT): sys.exit(OUT + " exists")


def bare(s): return HAR.sub("", unicodedata.normalize("NFC", s or "")).replace("أ", "ا").replace("إ", "ا")


def mut_form(v):
    b, raw = bare(v), unicodedata.normalize("NFC", v)
    if b.startswith("ان"): return "انْفَعَلَ"
    if b.startswith("است"): return "اسْتَفْعَلَ"
    if b.startswith("ا") and len(b) >= 5: return "افْتَعَلَ"
    if b.startswith("ت") and len(b) == 5 and b[2] == "ا": return "تَفَاعَلَ"
    if b.startswith("ت") and len(b) == 5: return "تَفَعْلَلَ"
    if b.startswith("ت") and "ّ" in raw: return "تَفَعَّلَ"
    if len(b) == 3: return "فَعَلَ"
    return ""


OK = {"تَفَعَّلَ": {"فَعَّلَ"}, "تَفَاعَلَ": {"فَاعَلَ"}, "تَفَعْلَلَ": {"فَعْلَلَ"},
      "انْفَعَلَ": {"فَعَلَ", "فَعِلَ", "فَعُلَ", "أَفْعَلَ"}, "افْتَعَلَ": {"فَعَلَ", "فَعِلَ", "فَعُلَ", "أَفْعَلَ"},
      "فَعَلَ": {"أَفْعَلَ", "فَعَّلَ"}}
rows = list(csv.DictReader(open(V1, encoding="utf-8"), delimiter="\t"))
cols = list(rows[0]) + ["base_status"]
for r in rows: r["base_status"] = "OK"
have = {(r["base"], r["mutawaa"]) for r in rows}
add = st_ok = st_un = 0
for p in csv.DictReader(open(POOL, encoding="utf-8"), delimiter="\t"):
    mf = mut_form(p["mutawi"]); bf = p["base_form"].split(" ")[0]
    good = bf in OK.get(mf, set())
    base = p["base"] if good else ""
    if (base, p["mutawi"]) in have: continue
    rows.append(dict(root=p["root"], base=base, base_form=bf if good else "", mutawaa=p["mutawi"], mutawaa_form=mf,
                     athar=p["athar"], athar_src="AHDATH_R1W" if p["athar"] else "MISSING", route="R1W_WASIT",
                     n_lex=p["n_lex"], lexicons="", evidence="wasit: مطاوع " + p["base_text"], gold_R1="",
                     base_event=p["base_event"] if good else "", mutawaa_event=p["mutawi_event"], rank="CANDIDATE",
                     base_status="OK" if good else "BASE_UNRESOLVED"))
    add += 1; st_ok += good; st_un += (not good)
with open(OUT, "w", encoding="utf-8") as f:
    w = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)
print(len(rows), "rows; R1W added", add, "base OK", st_ok, "BASE_UNRESOLVED", st_un, "->", OUT)
