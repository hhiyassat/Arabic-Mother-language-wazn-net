#!/usr/bin/env python3
"""build_mutawaa_v5.py — المطاوعة على أحدث إصدار HFN (v45) (المالك 2026-11-08: «اكمل باسلوب العلماء والمراجع»).

v1–v4 بُنيت على HFN v36/v37، فلم تُغطّ الأحداث الجديدة. هنا تُعاد سلسلة البناء نفسها (build_mutawaa → _v3 → _v4) بلا تغيير
في قواعدها، في مجلّد مؤقّت، على الإصدار الأحدث وحوض R1W المعاد بناؤه عليه (AMLN ahdath/mutawaa_wasit.py)، مع إصلاحين
لهمزة الوصل «ٱ» التي يكتبها HFN v44+ (حكم المالك 2026-11-07)، وإلا ضاع شيء:
  - build_mutawaa: مفتاح عيّنة R1 (gold_R1_MUTAWAA) مكتوب بالألف، فلم يُسقط حكمَا NOT؛ يُطابَق بـ ٱ = ا.
  - build_mutawaa_v4: letters() لا تعدّ ٱ ألفاً، فتُرك تصحيح التشكيل في انكشط وانتصب وانهشم؛ يُطابَق بـ ٱ = ا.
ثم يُقارن الناتج بـ data/mutawaa_v4.tsv على المفتاح (الجذر، الأصل، المطاوع؛ ٱ = ا):
  صفوف v4 كلّها تبقى كما هي (لا يُحذف شيء ولا يُكتب فوقه)؛
  صفّ جديد يدخل v5 إذا قرأه قارئان أعميان فقالا YES (evidence/mutawaa_v5_census/MUT7*.tsv): basis_v5=NEW_ON_v45_READ2؛
  صفّ قديم تغيّر فيه بيان المسلك وحده (+R1W_WASIT لأنّ الوسيط صار يشهد له) يُسجَّل في evidence/mutawaa_v4_to_v5.tsv ولا يُعدَّل.
المخرَج data/mutawaa_v5.tsv. CANDIDATE. يرفض الكتابة فوق ملف قائم.
Usage: python3 scripts/build_mutawaa_v5.py  (يحتاج AMLN على فرع فيه إصلاح ٱ في ahdath/ext/wasit_frames.py)"""
import csv, os, re, shutil, subprocess, sys, tempfile
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NET = os.environ.get("ARABIC_NET_HOME", os.path.dirname(H))
AMLN = os.path.join(NET, "Arabic-Mother-language-net")
OUT, V4 = H + "/data/mutawaa_v5.tsv", H + "/data/mutawaa_v4.tsv"
CEN = H + "/evidence/mutawaa_v5_census/"
if os.path.exists(OUT): sys.exit(OUT + " exists")
sys.path.insert(0, AMLN)
from hfn_release import hfn_release_dir  # noqa: E402
REL = os.path.basename(hfn_release_dir())

tmp = tempfile.mkdtemp(prefix="mutawaa_v5_")
# 1. حوض R1W على الإصدار الأحدث (نسخة مؤقّتة من ahdath؛ العيّنة المكتوبة هناك تُهمل)
shutil.copytree(os.path.join(AMLN, "ahdath"), os.path.join(tmp, "ahdath"))
code = ("import sys,runpy; sys.path.insert(0,'.'); sys.path.insert(1,%r); sys.argv=['x']; "
        "runpy.run_path('mutawaa_wasit.py', run_name='__main__')" % AMLN)
subprocess.run([sys.executable, "-c", code], cwd=os.path.join(tmp, "ahdath"), check=True, capture_output=True)
POOL = os.path.join(tmp, "ahdath", "mutawaa_R1W_pool.tsv")
# 2. السلسلة نفسها بمسارات مؤقّتة
os.makedirs(os.path.join(tmp, "scripts")); os.makedirs(os.path.join(tmp, "data"))
for v in ("", "_v3", "_v4"):
    s = open(H + f"/scripts/build_mutawaa{v}.py", encoding="utf-8").read()
    s = re.sub(r"release/release_v3[67]/", f"release/{REL}/", s)
    s = s.replace("~/arabic-net/Arabic-Mother-language-net/ahdath/mutawaa_R1W_pool.tsv", POOL)
    s = s.replace("~/arabic-net/Arabic-Mother-language-net/qabiliyyat", os.path.join(AMLN, "qabiliyyat"))
    if v == "":
        a = 'lab = gold.get((r["candidate"], r["base"]), "")'
        assert a in s; s = s.replace(a, 'lab = gold.get((r["candidate"].replace("ٱ", "ا"), r["base"]), "")')
    if v == "_v4":
        a = 'def letters(s): return HAR.sub("", nfc(s))'
        assert a in s; s = s.replace(a, 'def letters(s): return HAR.sub("", nfc(s)).replace("ٱ", "ا")')
    open(os.path.join(tmp, "scripts", f"build_mutawaa{v}.py"), "w", encoding="utf-8").write(s)
    subprocess.run([sys.executable, os.path.join(tmp, "scripts", f"build_mutawaa{v}.py")], check=True, capture_output=True)
NEW = os.path.join(tmp, "data", "mutawaa_v4.tsv")

def L(p): return list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))
def k(r): return (r["root"], r["base"].replace("ٱ", "ا"), r["mutawaa"].replace("ٱ", "ا"))
def w(r): return {c: (v or "").replace("ٱ", "ا") for c, v in r.items()}
old, new = L(V4), L(NEW)
ko, kn = {k(r): r for r in old}, {k(r): r for r in new}
gone = [x for x in ko if x not in kn]
# census of the added rows
def t(n): return {r["mid"]: r for r in csv.DictReader(open(CEN + n, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)}
IN, R1, R2 = t("MUT7.tsv"), t("MUT7_R1.tsv"), t("MUT7_R2.tsv")
ok = {(IN[m]["root"], IN[m]["base"], IN[m]["mutawi"]): R1[m]["verdict"] == R2[m]["verdict"] == "YES" for m in IN}
cols = list(old[0]) + ["basis_v5"]
rows = [dict(r, basis_v5="V4") for r in old]
added, refused, diff = [], [], []
for x, r in kn.items():
    if x in ko:
        cs = [c for c in ko[x] if w(ko[x]).get(c) != w(r).get(c)]
        if cs: diff.append(dict(root=x[0], base=x[1], mutawaa=x[2], change="PROVENANCE_ONLY:" + ",".join(cs),
                                v4=" | ".join(ko[x][c] for c in cs), on_v45=" | ".join(r.get(c, "") for c in cs)))
        continue
    pool_key = next((p for p in ok if p[0] == r["root"] and p[1].replace("ٱ", "ا") == x[1]), None)
    if pool_key and ok[pool_key]:
        rows.append({**{c: r.get(c, "") for c in cols}, "basis_v5": "NEW_ON_v45_READ2"}); added.append(x)
    else:
        refused.append(x)
    diff.append(dict(root=x[0], base=x[1], mutawaa=x[2], change="NEW_ON_v45:" + ("ADDED_READ2" if x in added else "NOT_ADDED"),
                     v4="", on_v45=r["route"]))
for x in gone: diff.append(dict(root=x[0], base=x[1], mutawaa=x[2], change="ABSENT_ON_v45_KEPT", v4=ko[x]["route"], on_v45=""))
with open(OUT, "w", encoding="utf-8", newline="") as f:
    wr = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n"); wr.writeheader(); wr.writerows(rows)
with open(H + "/evidence/mutawaa_v4_to_v5.tsv", "w", encoding="utf-8", newline="") as f:
    wr = csv.DictWriter(f, ["root", "base", "mutawaa", "change", "v4", "on_v45"], delimiter="\t", lineterminator="\n")
    wr.writeheader(); wr.writerows(diff)
shutil.rmtree(tmp)
print(REL, "v4", len(old), "rebuilt", len(new), "added", len(added), "not added", len(refused), "absent kept", len(gone),
      "provenance-only", sum(1 for d in diff if d["change"].startswith("PROVENANCE")), "→", OUT)
