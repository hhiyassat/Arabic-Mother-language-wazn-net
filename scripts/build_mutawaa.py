#!/usr/bin/env python3
"""build_mutawaa.py — الحقل الثاني: صلة الفعل بمطاوعه، فعلاً بفعل من المسموع (خطة الحقول الخمسة، المالك 2026-11-05).

المخرَج: data/mutawaa.tsv — (الفعل، المطاوع، مصدر المطاوع = اسم الأثر) مع المصدر والسند. لا يُستنتج بالوزن.
المسلكان (قراءة فقط):
  R1_QABILIYYAT  ~/arabic-net/Arabic-Mother-language-net/qabiliyyat/candidates_R1_MUTAWAA.tsv
                 (انْفَعَلَ ← فَعَلَ، 231 زوجاً، مقيس 0.964 على gold_R1_MUTAWAA.tsv). يُسقَط ما حُكم فيه NOT.
  LEX_FORMULA    عبارة المعجميين «فَعَلْتُهُ فانْفَعَلَ» في معاجم ~/roots (*_out/*-root-meanings-v2.jsonl)،
                 والطرفان حدثان في HFN v36 من الجذر نفسه، والتشكيل في النص يحسم بين أفعال الهيكل الواحد؛
                 ما بقي ملتبساً يُسقط. أي وزنين (انفعل/افتعل/تفعّل/تفاعل، والمجرد جواباً لأفعل/فعّل).
مصدر المطاوع من events.masdar في HFN؛ الفارغ يبقى فارغاً (athar_src=MISSING) ولا يُولَّد.
كل صفّ CANDIDATE. الاستعمال: python3 scripts/build_mutawaa.py   (يرفض الكتابة فوق ملف قائم)
"""
import csv, glob, json, os, re, sys, unicodedata, collections as C

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "mutawaa.tsv")
HFN = os.path.expanduser("~/arabic-net/HusseinFrameNet/release/release_v36/events.csv")
QAB = os.path.expanduser("~/arabic-net/Arabic-Mother-language-net/qabiliyyat")
ROOTS = os.path.expanduser("~/roots")
HAR = "ً-ْٰـ"
H = re.compile("[" + HAR + "]")
PAT = re.compile(r"(\S+?)ت[" + HAR + r"]*ه[" + HAR + r"]*(?:ا|م)?[" + HAR + r"]*\s+ف[" + HAR + r"]*(\S+)")


def nf(s):
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ٱ", "ا"), ("ى", "ي"), ("ـ", "")):
        s = s.replace(a, b)
    return unicodedata.normalize("NFC", s)


def sk(s):
    return H.sub("", nf(s))


def marks(s):
    out = []
    for ch in nf(s):
        if H.match(ch):
            if out:
                out[-1][1].add(ch)
        else:
            out.append([ch, set()])
    return out


def compatible(raw, verb):
    # الشدّة تفرّق فَعَلَ من فَعَّلَ: إن شُكِّل النص فالشدّة يجب أن تتطابق (قراءة العيّنة: 3 أخطاء من هذا)
    if voc(raw) and (("\u0651" in raw) != ("\u0651" in verb)):
        return False
    a, b = marks(raw), marks(verb)
    if len(a) != len(b):
        return False
    for (x, mx), (y, my) in zip(a, b):
        mx, my = mx - {"ْ"}, my - {"ْ"}
        if x != y or (mx and my and mx != my):
            return False
    return True


def voc(raw):
    return len(H.findall(raw)) >= 2


def main():
    if os.path.exists(OUT):
        sys.exit(OUT + " exists — not overwritten")
    E = list(csv.DictReader(open(HFN, encoding="utf-8")))
    Ei = {e["event_id"]: e for e in E}
    V = C.defaultdict(list)
    for e in E:
        V[(e["root_K"], sk(e["verb"]))].append(e)
    roots_of = C.defaultdict(set)
    for (rk, s) in V:
        roots_of[s].add(rk)
    rows = {}

    # R1
    gold = {(g["candidate"], g["base"]): g["label"]
            for g in csv.DictReader(open(QAB + "/gold_R1_MUTAWAA.tsv", encoding="utf-8"), delimiter="\t")}
    dropped = 0
    for r in csv.DictReader(open(QAB + "/candidates_R1_MUTAWAA.tsv", encoding="utf-8"), delimiter="\t"):
        lab = gold.get((r["candidate"], r["base"]), "")
        if lab == "NOT":
            dropped += 1
            continue
        te = Ei[r["event_id"]]
        bes = [e for e in V[(r["root"], sk(r["base"]))] if compatible(r["base"], e["verb"])]
        be = bes[0] if len(bes) == 1 else None
        rows[(be["event_id"] if be else r["base"], te["event_id"])] = dict(
            root=r["root"], base=r["base"], base_form=be["form"] if be else "", mutawaa=te["verb"],
            mutawaa_form=te["form"], athar=te["masdar"], athar_src="HFN_MASDAR" if te["masdar"] else "MISSING",
            route="R1_QABILIYYAT", n_lex=r["n_lex"], lexicons=r["lexicons"],
            evidence=r["gloss"], gold_R1=lab, base_event=be["event_id"] if be else "", mutawaa_event=te["event_id"])

    # LEX_FORMULA
    pairs, cites = C.defaultdict(set), C.defaultdict(list)
    for f in sorted(glob.glob(ROOTS + "/*_out/*-root-meanings-v2.jsonl")):
        lex = os.path.basename(os.path.dirname(f)).replace("_out", "")
        for line in open(f, encoding="utf-8"):
            rec = json.loads(line)
            for s in rec["sources"].values():
                for blk in (s.get("claims") or []) + (s.get("evidence") or []):
                    for m in PAT.finditer(blk.get("text") or ""):
                        braw = m.group(1)
                        if braw.startswith("و") and len(sk(braw)) > 3:
                            braw = braw[1:]
                        traw = m.group(2).strip('".,،:؛)(«»')
                        b, t = sk(braw), sk(traw)
                        if b == t:
                            continue
                        for rk in roots_of.get(b, set()) & roots_of.get(t, set()):
                            bs = [e for e in V[(rk, b)] if not voc(braw) or compatible(braw + "َ", e["verb"])
                                  or compatible(braw, e["verb"][:-1])]
                            ts = [e for e in V[(rk, t)] if not voc(traw) or compatible(traw, e["verb"])]
                            if len(bs) != 1 or len(ts) != 1 or bs[0]["event_id"] == ts[0]["event_id"]:
                                continue
                            # تَفَعَّلَ يطاوع فَعَّلَ لا فَعَلَ (الصحاح: كسرته فانكسر، وكسّرته فتكسّر)
                            if ts[0]["form"].startswith("تَفَعَّلَ") and bs[0]["form"].split(" ")[0] == "فَعَلَ":
                                continue
                            k = (bs[0]["event_id"], ts[0]["event_id"])
                            pairs[k].add(lex)
                            if len(cites[k]) < 2:
                                cites[k].append(lex + ": " + " ".join(m.group(0).split())[:60])
    both = 0
    for (b, t), lx in pairs.items():
        be, te = Ei[b], Ei[t]
        if (b, t) in rows:
            rows[(b, t)]["route"] += "+LEX_FORMULA"
            rows[(b, t)]["evidence"] += " | " + " | ".join(cites[(b, t)])
            both += 1
            continue
        rows[(b, t)] = dict(
            root=be["root_K"], base=be["verb"], base_form=be["form"], mutawaa=te["verb"], mutawaa_form=te["form"],
            athar=te["masdar"], athar_src="HFN_MASDAR" if te["masdar"] else "MISSING", route="LEX_FORMULA",
            n_lex=str(len(lx)), lexicons="·".join(sorted(lx)), evidence=" | ".join(cites[(b, t)]), gold_R1="",
            base_event=b, mutawaa_event=t)

    cols = ["root", "base", "base_form", "mutawaa", "mutawaa_form", "athar", "athar_src", "route", "n_lex",
            "lexicons", "evidence", "gold_R1", "base_event", "mutawaa_event", "rank"]
    out = sorted(rows.values(), key=lambda r: (r["root"], r["base"], r["mutawaa"]))
    with open(OUT, "w", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in out:
            w.writerow({**r, "rank": "CANDIDATE"})
    print(len(out), "rows ->", OUT, "| R1 NOT dropped", dropped, "| in both routes", both,
          C.Counter(r["route"] for r in out), C.Counter(r["athar_src"] for r in out))


if __name__ == "__main__":
    main()
