"""
classify.py — مصنِّف نوع الجذر من صورة الفعل لا من الجذر وحده (ملاحظة ahdath ٢، خطة المالك 2026-11-05).

الإعلال يُعرف من اللفظ: قَالَ أجوف (ألف وسط فعل ثلاثي الحروف)، وعَوِرَ صحيح العين (الواو ظاهرة).
  مضعّف  : العين = اللام والشدّة ظاهرة (مَرَّ)
  أجوف   : العين و/ي وفي اللفظ ألف وسطى (قَالَ، بَاعَ، خَافَ)
  ناقص   : اللام و/ي وآخر اللفظ ا/ى/ي (دَعَا، رَمَى، رَضِيَ)، أو واو ظاهرة في فَعُلَ (سَرُوَ)
  مثال   : الفاء و/ي (وَصَلَ، يَسَرَ)
  صحيح  : ما سوى ذلك، ومنه حرف العلّة الظاهر صحيحاً (عَوِرَ، صَيِدَ)
يُرفض صراحةً (Unsupported): غير الثلاثي، واللفيف، والمهموز مع إعلال أو تضعيف (رَأَى، شَاءَ، أَدَّ).
المهموز السالم (أَكَلَ، سَأَلَ، قَرَأَ) يُعاد SAHIH مع mahmuz=True؛ وما يبنيه المحرك منه تقرّره check_supported.
ما لا يطابق قاعدة يُرفض (NO_RULE) ولا يُخمَّن. CANDIDATE.
"""
from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

from core.types import RootType, Baab
from core.support import Unsupported

HAR = re.compile("[ً-ْٰـ]")
WEAK = set("وي")
HAMZA_SEATS = str.maketrans({"أ": "ء", "إ": "ء", "ؤ": "ء", "ئ": "ء", "آ": "ء", "ى": "ي"})
SHADDA = "ّ"


@dataclass(frozen=True)
class RootClass:
    root_type: RootType
    mahmuz: bool = False
    rank: str = "CANDIDATE"


def _bare(s: str) -> str:
    return HAR.sub("", unicodedata.normalize("NFC", s or ""))


def root_letters(root: str) -> str:
    return _bare(root).translate(HAMZA_SEATS)


def classify(root: str, verb: str) -> RootClass:
    """نوع الجذر للفعل الثلاثي المجرّد من جذره ولفظه. يرفع Unsupported لما لا يُبنى أو لا قاعدة له."""
    L = root_letters(root)
    if len(L) != 3:
        raise Unsupported("NOT_TRILITERAL", f"الجذر ليس ثلاثياً: {root}")
    a, b, c = L
    vb = _bare(verb)
    if not vb:
        raise Unsupported("NO_RULE", f"لا لفظ للفعل: {root}")
    if (a in WEAK and (b in WEAK or c in WEAK)) or (b in WEAK and c in WEAK):
        raise Unsupported("LAFIF", f"لفيف: {root} {verb}")
    mahmuz = "ء" in L
    if mahmuz and (b == c or b in WEAK or c in WEAK or a in WEAK):
        raise Unsupported("MAHMUZ", f"مهموز مع إعلال أو تضعيف: {root} {verb}")

    if b == c:
        if SHADDA in verb or len(vb) == 2:
            return RootClass(RootType.MUDAAF, mahmuz)
        return RootClass(RootType.SAHIH, mahmuz)          # مفكوك ظاهر: الحرفان في اللفظ
    if b in WEAK:
        if len(vb) == 3 and vb[1] == "ا":
            return RootClass(RootType.AJWAF_WAW if b == "و" else RootType.AJWAF_YAA, mahmuz)
        if len(vb) == 3 and vb[1] == b:
            return RootClass(RootType.SAHIH, mahmuz)      # عَوِرَ: العين ظاهرة صحيحة
        raise Unsupported("NO_RULE", f"عين معتلّة بلا قاعدة: {root} {verb}")
    if c in WEAK:
        if vb[-1] in "اىي":
            return RootClass(RootType.NAQIS_WAW if c == "و" else RootType.NAQIS_YAA, mahmuz)
        if c == "و" and vb[-1] == "و":
            # فَعُلَ من الناقص الواوي تبقى واوه: سَرُوَ، رَخُوَ (قراءة العيّنة: 5 أخطاء NO_RULE)
            return RootClass(RootType.NAQIS_WAW, mahmuz)
        raise Unsupported("NO_RULE", f"لام معتلّة بلا قاعدة: {root} {verb}")
    if a == "و":
        return RootClass(RootType.MITHAL_WAW, mahmuz)
    if a == "ي":
        return RootClass(RootType.MITHAL_YAA, mahmuz)
    return RootClass(RootType.SAHIH, mahmuz)


# حركة عين الماضي من صيغة HFN (الباب الكامل يحتاج حركة المضارع، وهي غير مسجّلة في HFN)
PAST_BAAB = {"فَعَلَ": Baab.FAA_YAF_U, "فَعِلَ": Baab.FAI_YAF_A, "فَعُلَ": Baab.FAU_YAF_U}


def past_baab(form: str) -> Optional[Baab]:
    """باب يكفي لتصريف الماضي من صيغة HFN؛ None إن لم تُحسم حركة العين (فَعَلَ/فَعِلَ)."""
    f = (form or "").split(" ")[0]
    if f == "فَعَّ":
        return Baab.FAA_YAF_U
    return PAST_BAAB.get(f)
