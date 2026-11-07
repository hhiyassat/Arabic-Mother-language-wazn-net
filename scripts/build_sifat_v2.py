#!/usr/bin/env python3
"""build_sifat_v2.py — v2 (2026-11-08): منطق build_sifat.py كما هو على أحدث إصدار من HFN بدل v36، وٱ = ا في المطابقة.
data/sifat.tsv لا يُمسّ؛ الفرق في evidence/sifat_v1_to_v2.tsv.
build_sifat.py — الحقل الرابع: صيغ الحدوث والثبوت والتكرار من المسموع (خطة الحقول الخمسة، المالك 2026-11-05).

المسموع: عبارة «فهو X، وY…» بعد معنى الفعل في المعجم الوسيط (M11، ~/roots/wasit_out)، والرأس يطابق فعل HFN v36 المجرّد
(الهيكل، والتشكيل إن وُجد، والشدّة). كل كلمة تُصنَّف بقالبها على حروف الجذر:
  حدوث  HUDUTH   فاعِل (ضَارِب)
  ثبوت  THUBUT   صفة مشبّهة: فَعِل، فَعْل، فَعَل، فُعْل، أَفْعَل، فَعْلان، فُعَال (حَسَن، حَزِن، أَحْمَر، عَطْشان، شُجَاع)
  تكرار TAKRAR   مبالغة: فَعَّال، مِفْعَال، مِفْعِيل، فِعِّيل (ضَرَّاب، مِهْذار)
  فَعِيل/فَعُول: ثبوت إن كان الفعل فَعُلَ أو لازماً (وسم الوسيط من data/transitivity_wasit.tsv)؛ وإلا AMBIG_FAIIL،
               لأنه من المتعدّي قد يكون مبالغة أو بمعنى مفعول (نَخِيس) — لا يُخمَّن.
  فاعِل من فَعُلَ صفة مشبّهة لا حدوث (طاهر). القراءة: evidence/sifat_sample60_judged.tsv.
  ما لا يطابق قالباً → OTHER (يُحفظ بسنده ولا يُصنَّف).
لا يُولَّد شيء: ما لا مسموع له لا يظهر. CANDIDATE. المخرَج data/sifat.tsv (يرفض الكتابة فوق ملف قائم).
"""
import csv, json, os, re, sys, unicodedata, collections as C

H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(H, "data", "sifat_v2.tsv")
TR = os.path.join(H, "data", "transitivity_wasit.tsv")
def _newest_release():
    """أحدث release_vN فيه MANIFEST (أو HFN_RELEASE) — نقل الطبقات من v36 إلى أحدث إصدار (المالك 2026-11-08)."""
    b = os.path.join(os.environ.get("ARABIC_NET_HOME", os.path.expanduser("~/arabic-net")), "HusseinFrameNet", "release")
    if os.environ.get("HFN_RELEASE"):
        return os.path.join(b, os.environ["HFN_RELEASE"])
    r = [d for d in os.listdir(b) if re.fullmatch(r"release_v\d+", d) and os.path.exists(os.path.join(b, d, "MANIFEST.json"))]
    return os.path.join(b, max(r, key=lambda d: int(d[9:])))
EV = os.path.join(_newest_release(), "events.csv")
WASIT = os.path.expanduser("~/roots/wasit_out/wasit-root-meanings-v2.jsonl")
HAR = re.compile("[ً-ْٰـ]")
SEATS = str.maketrans({"أ": "ء", "إ": "ء", "ؤ": "ء", "ئ": "ء", "آ": "ء", "ى": "ي"})
PAT = re.compile(r"ف(?:هو|هي|هى)\s+((?:[^\s.،:؛()]+)(?:\s*[،,]?\s*و[^\s.،:؛()]+){0,5})")
SH, DM, KS = "ّ", "ُ", "ِ"


def nfc(s):
    return unicodedata.normalize("NFC", s or "")


def bare(s):
    return HAR.sub("", nfc(s)).replace("ٱ", "ا").translate(SEATS).strip(" :،.-_")


def template(word, root):
    """القالب الصرفي للكلمة على حروف الجذر الثلاثة، أو None."""
    w, raw = bare(word), nfc(word)
    a, b, c = root
    if raw.startswith("آ") and a == "ء" and w[1:] == b + c:
        return "فاعل"                                   # آزِج = أَازِج (القارئ: كان يُقرأ فعل3)
    if len(w) == 4 and w[0] == a and w[1] == "ا" and w[3] == c and (w[2] == b or w[2] == "ء"):
        return "فاعل"
    if len(w) == 4 and w[0] == a and w[1] == b and w[2] == "ا" and w[3] == c:
        return "فعّال" if SH in raw else ("فُعال" if raw[1:2] == DM else "فَعال")
    if len(w) == 5 and w[0] == "م" and w[1:3] == a + b and w[3] == "ا" and w[4] == c:
        return "مفعال"
    if len(w) == 5 and w[0] == "م" and w[1:3] == a + b and w[3] == "ي" and w[4] == c:
        return "مفعيل"
    if len(w) == 4 and w[:2] == a + b and w[2] == "ي" and w[3] == c:
        return "فِعّيل" if SH in raw else "فعيل"
    if len(w) == 4 and w[:2] == a + b and w[2] == "و" and w[3] == c:
        return "فعول"
    if len(w) == 4 and w[0] == "ء" and w[1:] == a + b + c:
        return "أفعل"
    if len(w) == 5 and w[:3] == a + b + c and w[3:] == "ان":
        return "فعلان"
    if len(w) == 5 and w[:3] == a + b + c and w[3:] == "اء":
        return "فعلاء"
    if w == a + b + c:
        return "فعل3"
    if b == c and SH in raw and w == a + b:
        return "فعل3"                                   # مضعّف: لَبّ، غِرّ
    if b == c and SH in raw and w == "ء" + a + b:
        return "أفعل"                                   # أَقَبّ
    return None


KIND = {"فاعل": "HUDUTH", "فعّال": "TAKRAR", "مفعال": "TAKRAR", "مفعيل": "TAKRAR", "فِعّيل": "TAKRAR",
        "فُعال": "THUBUT", "أفعل": "THUBUT", "فعلاء": "THUBUT", "فعلان": "THUBUT", "فعل3": "THUBUT", "فَعال": "THUBUT"}


def main():
    if os.path.exists(OUT):
        sys.exit(OUT + " exists — not overwritten")
    trans = {r["event_id"]: r["transitivity_wasit"] for r in csv.DictReader(open(TR, encoding="utf-8"), delimiter="\t")}
    W = C.defaultdict(list)
    for line in open(WASIT, encoding="utf-8"):
        r = json.loads(line)
        k = bare(r["root"]["source_display"])
        for s in r["sources"].values():
            for c in s.get("claims") or []:
                if c.get("headword"):
                    W[k].append((c["headword"].strip(), c.get("text") or ""))
    rows, st = [], C.Counter()
    for e in csv.DictReader(open(EV, encoding="utf-8")):
        if e["layer"] not in ("الثلاثي", "المجرد"):
            continue
        root = bare(e["root_K"])
        if len(root) != 3:
            continue
        vb, vraw = bare(e["verb"]), nfc(e["verb"])
        for head, text in W.get(root, []):
            h0 = head.split()[0] if head.split() else ""
            if bare(h0) != vb or ((SH in h0) != (SH in vraw) and len(HAR.findall(h0)) >= 2):
                continue
            if len(HAR.findall(h0)) >= 2 and nfc(h0)[1:2] != vraw[1:2] and len(nfc(h0)) > 1 and HAR.match(nfc(h0)[1:2] or "x"):
                pass
            # حركة عين الماضي في الرأس، إن شُكِّل، تفرّق فَعَلَ/فَعِلَ/فَعُلَ
            hm = [ch for ch in nfc(h0) if HAR.match(ch) and ch != "ْ"]
            vm = [ch for ch in vraw if HAR.match(ch) and ch != "ْ"]
            if len(hm) >= 2 and hm[:2] != vm[:2]:
                continue
            for m in PAT.finditer(text):
                words = [x.strip(" ،,") for x in re.split(r"[،,]?\s+و(?=\S)", " " + m.group(1)) if x.strip(" ،,")]
                for w in words:
                    if bare(w) in ("هو", "هي", "في", "يقال", "المفعول", "به"):
                        continue                       # «وهي …» للمؤنث وأدوات، لا صفات
                    w = w.strip(" ،,").lstrip("و") if bare(w).startswith("و") and template(w, root) is None else w.strip(" ،,")
                    t = template(w, root)
                    kind = KIND.get(t)
                    if t in ("فعيل", "فعول"):
                        f = e["form"].split(" ")[0]
                        tr = trans.get(e["event_id"], "")
                        # من المتعدّي قد يكون مبالغةً أو بمعنى مفعول (نَخِيس، بَعِيج) — لا يُخمَّن
                        kind = "THUBUT" if (f == "فَعُلَ" or tr == "لازم") else "AMBIG_FAIIL"
                    if kind == "HUDUTH" and e["form"].split(" ")[0] == "فَعُلَ":
                        kind = "THUBUT"                # فاعل من فَعُلَ صفة مشبّهة (طاهر، خافض)
                    kind = kind or "OTHER"
                    st[kind] += 1
                    rows.append(dict(event_id=e["event_id"], root=e["root_K"], verb=e["verb"], form=e["form"],
                                     word=w, template=t or "", kind=kind, transitivity_wasit=trans.get(e["event_id"], ""),
                                     evidence=f"wasit: {h0} … فهو {m.group(1)[:50]}", rank="CANDIDATE"))
    seen, out = set(), []
    for r in rows:
        k = (r["event_id"], bare(r["word"]), r["kind"])
        if k not in seen:
            seen.add(k); out.append(r)
    with open(OUT, "w", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(out[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(out)
    print(len(out), "rows,", len({r["event_id"] for r in out}), "events ->", OUT)
    print(C.Counter(r["kind"] for r in out))


if __name__ == "__main__":
    main()
