"""
names_engine.py — الحقل الأول: اسم الفاعل واسم المفعول بشرط التعدّي (المجرّد والمزيد).

خطة الحقول الخمسة (المالك 2026-11-05) وتوصياته:
  - اسم الفاعل دائماً.
  - اسم المفعول للمتعدّي (maful_kind=DIRECT).
  - اللازم بحرف يُبنى بالجارّ: «مَمْرُور بِهِ» (maful_kind=BI_HARF). اسمٌ نحويّ لا يلزم منه أثرٌ في المحلّ.
  - اللازم بلا حرف: لا اسم مفعول (maful_kind=NONE).
  - «مشترك» يُبنى ويُعلَّم (flags=MUSHTARAK) ولا يُرفض (ضَرَبَ موسوم «مشترك» في HFN).
  - التعدّي غير المعلوم («غير محدد»، فارغ، None) يُرفض بخطأ صريح، لا يُخمَّن.
  - التعارض النحوي القطعي يُرفض: فَعُلَ متعدّياً، وانْفَعَلَ (VII) واِفْعَلَّ (IX) متعدّيين.

التعدّي مُدخَل من المستدعي، لا يستنتجه المحرك. وسم «متعدي» في HFN v36 لم يجتز القياس
(عيّنة ahdath gold_R2_v2: 35/49، ويلسون الأدنى 0.576 < 0.78)، فلا يُعتمد عليه دون مراجعة.
كل مخرَج CANDIDATE حتى يحكم DR_HUSSEIN.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.types import RootType, Baab
from core.support import check_supported
from engines.derivation_engine import _gen_ism_faail_I, _gen_ism_mafuul_I, _apply_wazn
from engines.rubai_engine import check_rubai, derive_rubai


class Transitivity(str, Enum):
    LAZIM     = "لازم"
    MUTAADDI  = "متعدي"
    MUSHTARAK = "مشترك"


class MafulKind(str, Enum):
    DIRECT  = "DIRECT"    # متعدٍّ بنفسه: مَكْتُوب
    BI_HARF = "BI_HARF"   # لازم بحرف: مَمْرُور بِهِ
    NONE    = "NONE"      # لازم بلا حرف: لا اسم مفعول


class TransitivityUnknown(ValueError):
    """التعدّي غير معلوم — يُرفض ولا يُخمَّن."""


class TransitivityConflict(ValueError):
    """وسم التعدّي يخالف حكماً نحوياً قطعياً في الوزن أو الباب."""


# حرف الجرّ ← الجارّ والمجرور بضمير الغائب (قائمة مغلقة؛ غيرها يُرفض)
HARF_PRONOUN = {
    "ب": "بِهِ", "على": "عَلَيْهِ", "في": "فِيهِ", "إلى": "إِلَيْهِ",
    "عن": "عَنْهُ", "من": "مِنْهُ", "ل": "لَهُ", "مع": "مَعَهُ",
}

# أوزان لا تكون إلا لازمة (حكم قطعي): انْفَعَلَ، اِفْعَلَّ
ALWAYS_LAZIM_WAZN = {"VII": "انْفَعَلَ", "IX": "اِفْعَلَّ",
                     "Q2": "تَفَعْلَلَ", "Q3": "اِفْعَنْلَلَ", "Q4": "اِفْعَلَلَّ"}   # مزيد الرباعي لازم


@dataclass(frozen=True)
class Names:
    letters:      str
    wazn:         str                  # "I" للمجرّد، أو II–X
    verb:         Optional[str]        # الماضي للمزيد؛ None للمجرّد (يحتاج الباب والتصريف)
    transitivity: Transitivity
    harf:         Optional[str]
    ism_faail:    str
    ism_mafuul:   Optional[str]
    maful_kind:   MafulKind
    flags:        tuple = ()
    rank:         str = "CANDIDATE"


_SEATS = str.maketrans({"أ": "ء", "إ": "ء", "ؤ": "ء", "ئ": "ء", "آ": "ء"})
F, D, K, S = "َ", "ُ", "ِ", "ْ"


def _mahmuz_names_I(a: str, b: str, c: str) -> tuple:
    """المهموز السالم في المجرّد، الهمزة على كرسيّها (منطق ahdath derive_thulathi، فرع MAHMUZ):
    فاء: آكِل / مَأْكُول · عين: سَائِل / مَسْؤُول · لام: قَارِئ / مَقْرُوء."""
    if a == "ء":
        return "آ" + b + K + c, "مَأْ" + b + D + "و" + c
    if b == "ء":
        return a + F + "ا" + "ئ" + K + c, "مَ" + a + S + "ؤ" + D + "و" + c
    return a + F + "ا" + b + K + "ئ", "مَ" + a + S + b + D + "و" + "ء"


def _transitivity(t) -> Transitivity:
    if isinstance(t, Transitivity):
        return t
    s = (t or "").strip()
    try:
        return Transitivity(s)
    except ValueError:
        raise TransitivityUnknown(f"التعدّي غير معلوم: {t!r} (المقبول: لازم/متعدي/مشترك)") from None


def derive_names(letters: str, root_type: RootType, wazn: str = "I",
                 transitivity=None, harf: Optional[str] = None,
                 baab: Optional[Baab] = None) -> Names:
    """اسما الفاعل والمفعول لفعلٍ واحد بشرط تعدّيه. يرفع خطأً صريحاً لما لا يُقاس."""
    if wazn.startswith("Q"):                                     # الرباعي (rubai_engine)
        check_rubai(letters, wazn)
    else:
        # الحقل الخامس؛ المهموز السالم مفتوح في المجرّد وحده (ملاحظة ahdath ١، المالك 2026-11-05)
        check_supported(letters, root_type, allow_sound_mahmuz=(wazn == "I"))
    letters = letters.translate(_SEATS)
    t = _transitivity(transitivity)
    if t is not Transitivity.LAZIM and harf:
        raise TransitivityConflict(f"الحرف {harf!r} لا يُعطى إلا مع «لازم» (التعدّي: {t.value})")
    if harf is not None and harf not in HARF_PRONOUN:
        raise ValueError(f"حرف جرّ غير معروف: {harf!r} (المعروف: {sorted(HARF_PRONOUN)})")
    if t is not Transitivity.LAZIM:
        if wazn in ALWAYS_LAZIM_WAZN:
            raise TransitivityConflict(f"{ALWAYS_LAZIM_WAZN[wazn]} لا يكون إلا لازماً: {letters} موسوم {t.value}")
        if wazn == "I" and baab == Baab.FAU_YAF_U:
            raise TransitivityConflict(f"فَعُلَ لا يكون إلا لازماً: {letters} موسوم {t.value}")

    if wazn.startswith("Q"):
        f = derive_rubai(letters, wazn)
        verb, faail, mafuul = f["verb"], f["ism_faail"], f["ism_mafuul"]
    elif wazn == "I" and "ء" in letters:
        verb, (faail, mafuul) = None, _mahmuz_names_I(*letters)
    elif wazn == "I":
        r1, r2, r3 = letters
        verb, faail, mafuul = None, _gen_ism_faail_I(r1, r2, r3, root_type), _gen_ism_mafuul_I(r1, r2, r3, root_type)
    else:
        r1, r2, r3 = letters
        f = _apply_wazn(wazn, r1, r2, r3, root_type)           # يرفع لمفتاح وزن مجهول
        verb, faail, mafuul = f["verb"], f["i_faail"], f["i_mafuul"]

    flags = ("MUSHTARAK",) if t is Transitivity.MUSHTARAK else ()
    if t is Transitivity.LAZIM:
        if harf:
            return Names(letters, wazn, verb, t, harf, faail, f"{mafuul} {HARF_PRONOUN[harf]}", MafulKind.BI_HARF, flags)
        return Names(letters, wazn, verb, t, None, faail, None, MafulKind.NONE, flags)
    return Names(letters, wazn, verb, t, None, faail, mafuul, MafulKind.DIRECT, flags)
