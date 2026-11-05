"""
support.py — الحقل الخامس: الرفض الصريح (fail-closed) لما لا يُقاس في المحرك.
ما لا مُصرِّف له يُرفض بخطأ صريح، لا يُعامَل بصمت كالصحيح ولا يُخمَّن.
خطة الحقول الخمسة، المالك 2026-11-05. CANDIDATE.
"""
from core.types import RootType

HAMZA = set("ءأإؤئآ")
UNSUPPORTED_TYPES = (RootType.LAFIF_MAQRUN, RootType.LAFIF_MAFRUQ)


class Unsupported(NotImplementedError):
    """جذر لا يبنيه المحرك؛ code يسمّي السبب (LAFIF / NOT_TRILITERAL / MAHMUZ)."""
    def __init__(self, code: str, msg: str):
        super().__init__(f"[{code}] {msg}")
        self.code = code


def is_sound_mahmuz(letters: str, root_type: RootType) -> bool:
    """مهموز سالم: همزة واحدة، بلا حرف علّة ولا تضعيف، والنوع صحيح (أكل، سأل، قرأ)."""
    L = letters.translate(str.maketrans({"أ": "ء", "إ": "ء", "ؤ": "ء", "ئ": "ء", "آ": "ء"}))
    return (len(L) == 3 and L.count("ء") == 1 and root_type == RootType.SAHIH
            and not (set(L) & set("وي")) and L[1] != L[2])


def check_supported(letters: str, root_type: RootType, allow_sound_mahmuz: bool = False) -> None:
    if len(letters) != 3:
        raise Unsupported("NOT_TRILITERAL", f"الجذر يجب أن يكون ثلاثياً، والرباعي غير مدعوم: {letters}")
    if root_type in UNSUPPORTED_TYPES:
        raise Unsupported("LAFIF", f"لا مُصرِّف لنوع الجذر {root_type.value}: {letters}")
    if HAMZA & set(letters) and not (allow_sound_mahmuz and is_sound_mahmuz(letters, root_type)):
        # رسم الهمزة (أَخَذَ لا ءَخَذَ، آخِذ، يَسْأَلُ، قَارِئ) وتخفيفها (يَرَى، خُذْ) غير مبنيَّين.
        # يشمل المهموز المعتلّ (رَأَى) والمزيد المهموز (أَطْفَأَ).
        raise Unsupported("MAHMUZ", f"المهموز غير مدعوم (رسم الهمزة وتخفيفها غير مبنيَّين): {letters}")
