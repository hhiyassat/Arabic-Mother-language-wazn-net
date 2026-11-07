"""
rubai_engine.py — الرباعي المجرّد ومزيده (طلب المالك 2026-11-05: «نعم، أضف الرباعي»).

الأوزان (data/awzaan_af3aal_all.csv):
  Q1  فَعْلَلَ    يُفَعْلِلُ     دَحْرَجَ يُدَحْرِجُ        W07  مصدر: فَعْلَلَة / فِعْلَال
  Q2  تَفَعْلَلَ  يَتَفَعْلَلُ   تَدَحْرَجَ يَتَدَحْرَجُ    W27  مصدر: تَفَعْلُل
  Q3  اِفْعَنْلَلَ يَفْعَنْلِلُ  اِحْرَنْجَمَ يَحْرَنْجِمُ   W28  مصدر: اِفْعِنْلَال
  Q4  اِفْعَلَلَّ  يَفْعَلِلُّ    اِقْشَعَرَّ يَقْشَعِرُّ      W29  مصدر: اِفْعِلَّال (اِقْشِعْرَار)

الجذر أربعة أحرف أصول (دحرج، حرجم، قشعر). همزة الوصل تُكتب ألفاً بحركة البدء (C3).
يُرفض صراحةً (Unsupported): غير الرباعي، والمهموز (رسم الهمزة غير مبنيّ: اِطْمَأَنَّ)، وما آخره حرف علّة.
الملحقات (فَوْعَلَ، فَيْعَلَ، تَفَعْلَى…) ليست هنا. كل مخرَج CANDIDATE.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.types import RootType, Baab
from core.support import Unsupported, HAMZA, rasm_wasl
from engines.morphological_engine import (ConjugationParadigm, _cells, PAST_ACT_SFX, PRES_PREFIX,
                                          PRES_MARFUU, PRES_MANSUB, PRES_MAJZUM, IMP_SFX, F, D, K, S, SH, A,
                                          merge_nun)

W, Y = "و", "ي"
RUBAI_WAZN = {"Q1": "فَعْلَلَ", "Q2": "تَفَعْلَلَ", "Q3": "اِفْعَنْلَلَ", "Q4": "اِفْعَلَلَّ"}
WAZN_BY_FORM = {"فَعْلَلَ": "Q1", "تَفَعْلَلَ": "Q2", "افْعَنْلَلَ": "Q3", "اِفْعَنْلَلَ": "Q3",
                "افْعَلَلَّ": "Q4", "اِفْعَلَلَّ": "Q4"}


def check_rubai(letters: str, wazn: str) -> None:
    if wazn not in RUBAI_WAZN:
        raise ValueError(f"وزن رباعي غير معروف: {wazn!r} (المعروف: {sorted(RUBAI_WAZN)})")
    if len(letters) != 4:
        raise Unsupported("NOT_QUADRILITERAL", f"الجذر ليس رباعياً: {letters}")
    if HAMZA & set(letters):
        raise Unsupported("MAHMUZ", f"الرباعي المهموز غير مدعوم (رسم الهمزة غير مبنيّ): {letters}")
    if letters[3] in (W, Y):
        raise Unsupported("NAQIS_RUBAI", f"الرباعي المعتلّ الآخر غير مدعوم: {letters}")


def _pre(pgn, vowel):
    return PRES_PREFIX[pgn][0] + vowel


# ── Q1–Q3: صيغ سالمة، الصيغة = بادئة + جذع + لاحقة ─────────────────────
def _stems(wazn, a, b, c, d):
    """(ماضٍ معلوم، ماضٍ مجهول، حركة حرف المضارعة، جذع المضارع المعلوم، جذع المضارع المجهول، جذع الأمر)"""
    if wazn == "Q1":
        return (a + F + b + S + c + F + d, a + D + b + S + c + K + d, D,
                a + F + b + S + c + K + d, a + F + b + S + c + F + d, a + F + b + S + c + K + d)
    if wazn == "Q2":
        return ("تَ" + a + F + b + S + c + F + d, "تُ" + a + D + b + S + c + K + d, F,
                "تَ" + a + F + b + S + c + F + d, "تَ" + a + F + b + S + c + F + d, "تَ" + a + F + b + S + c + F + d)
    # Q3
    return ("اِ" + a + S + b + F + "نْ" + c + F + d, "اُ" + a + S + b + D + "نْ" + c + K + d, F,
            a + S + b + F + "نْ" + c + K + d, a + S + b + F + "نْ" + c + F + d, "اِ" + a + S + b + F + "نْ" + c + K + d)


def _conj_regular(wazn, a, b, c, d):
    pa, pp, pv, ra, rp, imp = _stems(wazn, a, b, c, d)
    out = {
        ("ماضٍ", "معلوم"): [(pa + s, g) for g, s in PAST_ACT_SFX.items()],
        ("ماضٍ", "مجهول"): [(pp + s, g) for g, s in PAST_ACT_SFX.items()],
        ("مضارع مرفوع", "معلوم"): [(_pre(g, pv) + ra + s, g) for g, s in PRES_MARFUU.items()],
        ("مضارع مرفوع", "مجهول"): [(_pre(g, D) + rp + s, g) for g, s in PRES_MARFUU.items()],
        ("مضارع منصوب", "معلوم"): [(_pre(g, pv) + ra + s, g) for g, s in PRES_MANSUB.items()],
        ("مضارع مجزوم", "معلوم"): [(_pre(g, pv) + ra + s, g) for g, s in PRES_MAJZUM.items()],
        ("أمر", "معلوم"): [(imp + s, g) for g, s in IMP_SFX.items()],
    }
    return out


# ── Q4: اِفْعَلَلَّ — لامه مضعّفة: إدغام قبل المتحرّك وفكّ قبل الساكن (كالمضعّف) ──
def _conj_q4(a, b, c, d):
    """اِقْشَعَرَّ: يُدغم ما لم يتّصل به ضمير رفع متحرّك (اِقْشَعْرَرْتُ)، والجزم والأمر بالوجهين (C5)."""
    pm = "اِ" + a + S + b + F + c + F + d + SH          # اِقْشَعَرّ
    ps = "اِ" + a + S + b + F + c + S + d + F + d        # اِقْشَعْرَر
    ppm = "اُ" + a + S + b + D + c + K + d + SH         # اُقْشُعِرّ
    pps = "اُ" + a + S + b + D + c + S + d + K + d       # اُقْشُعْرِر
    rm, rs = a + S + b + F + c + K + d + SH, a + S + b + F + c + S + d + K + d      # قْشَعِرّ / قْشَعْرِر
    rpm, rps = a + S + b + F + c + F + d + SH, a + S + b + F + c + S + d + F + d    # المجهول

    def past(m, s):
        res = []
        for g, sfx in PAST_ACT_SFX.items():
            if g[0] == "غائب" and g[1] in ("مفرد", "مثنى"):
                res.append((m + sfx, g))
            elif g == ("غائب", "جمع", "مذكر"):
                res.append((m[:-1] + D + SH + W + A, g))          # اِقْشَعَرُّوا
            else:
                res.append((s + sfx, g))                          # اِقْشَعْرَرْتُ، اِقْشَعْرَرْنَ
        return res

    def pres(tbl, pv, m, s, jazm=False):
        res = []
        for g, sfx in tbl.items():
            p = _pre(g, pv)
            if sfx.startswith(S + "ن"):                           # يَقْشَعْرِرْنَ
                res.append((p + s + sfx, g))
            elif jazm and sfx == S:                               # يَقْشَعِرَّ / يَقْشَعْرِرْ
                res.append((p + m + F + "/" + p + s + S, g))
            elif sfx in (D, F):
                res.append((p + m + sfx, g))
            else:                                                 # انِ، ونَ، ينَ، وا، ي، ا
                res.append((p + m + sfx, g))
        return res

    imp = []
    for g, sfx in IMP_SFX.items():
        base_m, base_s = "اِ" + rm, "اِ" + rs
        if sfx == S:
            imp.append((base_m + F + "/" + base_s + S, g))        # اِقْشَعِرَّ / اِقْشَعْرِرْ
        elif sfx.startswith(S + "ن"):
            imp.append((base_s + sfx, g))                         # اِقْشَعْرِرْنَ
        else:
            imp.append((base_m + sfx, g))
    return {
        ("ماضٍ", "معلوم"): past(pm, ps),
        ("ماضٍ", "مجهول"): past(ppm, pps),
        ("مضارع مرفوع", "معلوم"): pres(PRES_MARFUU, F, rm, rs),
        ("مضارع مرفوع", "مجهول"): pres(PRES_MARFUU, D, rpm, rps),
        ("مضارع منصوب", "معلوم"): pres(PRES_MANSUB, F, rm, rs),
        ("مضارع مجزوم", "معلوم"): pres(PRES_MAJZUM, F, rm, rs, jazm=True),
        ("أمر", "معلوم"): imp,
    }


def conjugate_rubai(letters: str, wazn: str = "Q1") -> ConjugationParadigm:
    """النموذج الصرفي (90 خلية) للرباعي. الخلية ذات الوجهين مفصولة بـ / (C5)."""
    check_rubai(letters, wazn)
    a, b, c, d = letters
    tables = _conj_q4(a, b, c, d) if wazn == "Q4" else _conj_regular(wazn, a, b, c, d)
    p = ConjugationParadigm(root=letters, root_type=RootType.SAHIH, baab=Baab.FAA_YAF_U)
    for (mood, voice), pairs in tables.items():
        if d == "ن":
            pairs = [(merge_nun(f), g) for f, g in pairs]
        p.cells += _cells(pairs, mood, voice)
    return p


def derive_rubai(letters: str, wazn: str = "Q1") -> dict:
    """الفعل، والمصدر (بدائل بـ /)، واسم الفاعل، واسم المفعول — قياسية كلها. همزة الوصل ٱ (حكم المالك 2026-11-07)."""
    return {k: "/".join(rasm_wasl(x) for x in v.split("/")) for k, v in _derive_rubai_raw(letters, wazn).items()}


def _derive_rubai_raw(letters: str, wazn: str = "Q1") -> dict:
    check_rubai(letters, wazn)
    a, b, c, d = letters
    if wazn == "Q1":
        return dict(verb=a + F + b + S + c + F + d + F,
                    masdar=a + F + b + S + c + F + d + F + "ة" + "/" + a + K + b + S + c + F + A + d,
                    ism_faail="مُ" + a + F + b + S + c + K + d, ism_mafuul="مُ" + a + F + b + S + c + F + d)
    if wazn == "Q2":
        return dict(verb="تَ" + a + F + b + S + c + F + d + F, masdar="تَ" + a + F + b + S + c + D + d,
                    ism_faail="مُتَ" + a + F + b + S + c + K + d, ism_mafuul="مُتَ" + a + F + b + S + c + F + d)
    if wazn == "Q3":
        return dict(verb="اِ" + a + S + b + F + "نْ" + c + F + d + F, masdar="اِ" + a + S + b + K + "نْ" + c + F + A + d,
                    ism_faail="مُ" + a + S + b + F + "نْ" + c + K + d, ism_mafuul="مُ" + a + S + b + F + "نْ" + c + F + d)
    return dict(verb="اِ" + a + S + b + F + c + F + d + SH + F, masdar="اِ" + a + S + b + K + c + S + d + F + A + d,
                ism_faail="مُ" + a + S + b + F + c + K + d + SH, ism_mafuul="مُ" + a + S + b + F + c + F + d + SH)
