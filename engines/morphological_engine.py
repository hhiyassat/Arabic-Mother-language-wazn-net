"""
morphological_engine.py — المحرك الصرفي
يولِّد النموذج الصرفي الكامل للفعل الثلاثي المجرد
المبدأ الخامس: ما يمكن توليده لا يُخزَّن
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.types import RootType, Baab
from core.support import check_supported, rasm_wasl, ibtida


# ══════════════════════════════════════════════════════════════════════
# هياكل البيانات
# ══════════════════════════════════════════════════════════════════════

@dataclass
class ConjugationCell:
    """خلية تصريفية واحدة"""
    form:    str
    person:  str   # متكلم / مخاطب / غائب
    number:  str   # مفرد / مثنى / جمع
    gender:  str   # مذكر / مؤنث / -
    voice:   str   # معلوم / مجهول
    mood:    str   # ماضٍ / مضارع مرفوع / منصوب / مجزوم / أمر
    rule:    str = ""   # القاعدة الصوتية المطبَّقة
    ibtida:  str = ""   # حركة البدء بهمزة الوصل (ِ أو ُ) — الصورة نفسها ترسمها ٱ برسم المصحف (حكم المالك 2026-11-07)


@dataclass
class ConjugationParadigm:
    """النموذج الصرفي الكامل للجذر"""
    root:      str
    root_type: RootType
    baab:      Baab
    cells:     list[ConjugationCell] = field(default_factory=list)

    def filter(self, **kwargs) -> list[ConjugationCell]:
        result = self.cells
        for k, v in kwargs.items():
            result = [c for c in result if getattr(c, k) == v]
        return result

    def table(self, mood: str, voice: str = "معلوم") -> dict:
        cells = self.filter(mood=mood, voice=voice)
        return {(c.person, c.number, c.gender): c.form for c in cells}


# ══════════════════════════════════════════════════════════════════════
# الحركات — ثوابت Unicode
# ══════════════════════════════════════════════════════════════════════

F  = "َ"   # فتحة   U+064E
D  = "ُ"   # ضمة    U+064F
K  = "ِ"   # كسرة   U+0650
S  = "ْ"   # سكون   U+0652
SH = "ّ"   # شدة    U+0651

A  = "ا"   # ألف
W  = "و"   # واو
Y  = "ي"   # ياء
# ملاحظة: الشدة تُكتب قبل الحركة (SH + haraka)


def _r2_past_v(baab: Baab) -> str:
    if baab in (Baab.FAI_YAF_A, Baab.FAI_YAF_I): return K
    if baab == Baab.FAU_YAF_U: return D
    return F

def _r2_pres_v(baab: Baab) -> str:
    if baab in (Baab.FAA_YAF_U, Baab.FAU_YAF_U): return D
    if baab in (Baab.FAA_YAF_I, Baab.FAI_YAF_I):   return K
    return F


# ══════════════════════════════════════════════════════════════════════
# جداول اللواحق الموحَّدة (مشتركة بين المصرِّفات)
# ══════════════════════════════════════════════════════════════════════

# الماضي المعلوم — اللاحقة تُضاف بعد (ر١ + حركة + ر٢ + حركة + ر٣)
# (الحركة على ر٣ مدمجة في اللاحقة)
PAST_ACT_SFX = {
    ("غائب",  "مفرد",  "مذكر"): F,               # كَتَبَ
    ("غائب",  "مفرد",  "مؤنث"): F + "تْ",         # كَتَبَتْ
    ("غائب",  "مثنى",  "مذكر"): F + A,            # كَتَبَا
    ("غائب",  "مثنى",  "مؤنث"): F + "تَا",        # كَتَبَتَا
    ("غائب",  "جمع",   "مذكر"): D + W + A,        # كَتَبُوا
    ("غائب",  "جمع",   "مؤنث"): S + "نَ",         # كَتَبْنَ
    ("مخاطب", "مفرد",  "مذكر"): S + "تَ",         # كَتَبْتَ
    ("مخاطب", "مفرد",  "مؤنث"): S + "تِ",         # كَتَبْتِ
    ("مخاطب", "مثنى",  "مذكر"): S + "تُمَا",      # كَتَبْتُمَا
    ("مخاطب", "مثنى",  "مؤنث"): S + "تُمَا",
    ("مخاطب", "جمع",   "مذكر"): S + "تُمْ",       # كَتَبْتُمْ
    ("مخاطب", "جمع",   "مؤنث"): S + "تُنَّ",      # كَتَبْتُنَّ
    ("متكلم", "مفرد",  "-"):    S + "تُ",          # كَتَبْتُ
    ("متكلم", "جمع",   "-"):    S + "نَا",         # كَتَبْنَا
}

# الماضي المجهول — نفس اللواحق لكن الجذر مختلف (فُعِلَ)
PAST_PASS_SFX = PAST_ACT_SFX   # نفس البنية

# حروف المضارعة + حركتها
PRES_PREFIX = {
    ("غائب",  "مفرد",  "مذكر"): "يَ",
    ("غائب",  "مفرد",  "مؤنث"): "تَ",
    ("غائب",  "مثنى",  "مذكر"): "يَ",
    ("غائب",  "مثنى",  "مؤنث"): "تَ",
    ("غائب",  "جمع",   "مذكر"): "يَ",
    ("غائب",  "جمع",   "مؤنث"): "يَ",
    ("مخاطب", "مفرد",  "مذكر"): "تَ",
    ("مخاطب", "مفرد",  "مؤنث"): "تَ",
    ("مخاطب", "مثنى",  "مذكر"): "تَ",
    ("مخاطب", "مثنى",  "مؤنث"): "تَ",
    ("مخاطب", "جمع",   "مذكر"): "تَ",
    ("مخاطب", "جمع",   "مؤنث"): "تَ",
    ("متكلم", "مفرد",  "-"):    "أَ",
    ("متكلم", "جمع",   "-"):    "نَ",
}

# نواتج المضارع — اللاحقة تُضاف بعد ر٣ (الحركة على ر٣ مدمجة في اللاحقة)
PRES_MARFUU = {
    ("غائب",  "مفرد",  "مذكر"): D,                # يَكْتُبُ
    ("غائب",  "مفرد",  "مؤنث"): D,
    ("غائب",  "مثنى",  "مذكر"): F + A + "نِ",    # يَكْتُبَانِ
    ("غائب",  "مثنى",  "مؤنث"): F + A + "نِ",
    ("غائب",  "جمع",   "مذكر"): D + W + "نَ",    # يَكْتُبُونَ
    ("غائب",  "جمع",   "مؤنث"): S + "نَ",         # يَكْتُبْنَ
    ("مخاطب", "مفرد",  "مذكر"): D,
    ("مخاطب", "مفرد",  "مؤنث"): K + Y + "نَ",    # تَكْتُبِينَ
    ("مخاطب", "مثنى",  "مذكر"): F + A + "نِ",
    ("مخاطب", "مثنى",  "مؤنث"): F + A + "نِ",
    ("مخاطب", "جمع",   "مذكر"): D + W + "نَ",
    ("مخاطب", "جمع",   "مؤنث"): S + "نَ",
    ("متكلم", "مفرد",  "-"):    D,
    ("متكلم", "جمع",   "-"):    D,
}

PRES_MANSUB = {
    ("غائب",  "مفرد",  "مذكر"): F,                # يَكْتُبَ
    ("غائب",  "مفرد",  "مؤنث"): F,
    ("غائب",  "مثنى",  "مذكر"): F + A,            # يَكْتُبَا
    ("غائب",  "مثنى",  "مؤنث"): F + A,
    ("غائب",  "جمع",   "مذكر"): D + W + A,        # يَكْتُبُوا
    ("غائب",  "جمع",   "مؤنث"): S + "نَ",
    ("مخاطب", "مفرد",  "مذكر"): F,
    ("مخاطب", "مفرد",  "مؤنث"): K + Y,            # تَكْتُبِي
    ("مخاطب", "مثنى",  "مذكر"): F + A,
    ("مخاطب", "مثنى",  "مؤنث"): F + A,
    ("مخاطب", "جمع",   "مذكر"): D + W + A,
    ("مخاطب", "جمع",   "مؤنث"): S + "نَ",
    ("متكلم", "مفرد",  "-"):    F,
    ("متكلم", "جمع",   "-"):    F,
}

PRES_MAJZUM = {
    ("غائب",  "مفرد",  "مذكر"): S,                # يَكْتُبْ
    ("غائب",  "مفرد",  "مؤنث"): S,
    ("غائب",  "مثنى",  "مذكر"): F + A,
    ("غائب",  "مثنى",  "مؤنث"): F + A,
    ("غائب",  "جمع",   "مذكر"): D + W + A,
    ("غائب",  "جمع",   "مؤنث"): S + "نَ",
    ("مخاطب", "مفرد",  "مذكر"): S,
    ("مخاطب", "مفرد",  "مؤنث"): K + Y,
    ("مخاطب", "مثنى",  "مذكر"): F + A,
    ("مخاطب", "مثنى",  "مؤنث"): F + A,
    ("مخاطب", "جمع",   "مذكر"): D + W + A,
    ("مخاطب", "جمع",   "مؤنث"): S + "نَ",
    ("متكلم", "مفرد",  "-"):    S,
    ("متكلم", "جمع",   "-"):    S,
}

# لواحق الأمر (تُضاف بعد ر٣)
IMP_SFX = {
    ("مخاطب", "مفرد",  "مذكر"): S,                # اِكْتُبْ
    ("مخاطب", "مفرد",  "مؤنث"): K + Y,            # اِكْتُبِي
    ("مخاطب", "مثنى",  "مذكر"): F + A,            # اِكْتُبَا
    ("مخاطب", "مثنى",  "مؤنث"): F + A,
    ("مخاطب", "جمع",   "مذكر"): D + W + A,        # اِكْتُبُوا
    ("مخاطب", "جمع",   "مؤنث"): S + "نَ",         # اِكْتُبْنَ
}


# ══════════════════════════════════════════════════════════════════════
# الجذر الصحيح السالم
# ══════════════════════════════════════════════════════════════════════

class _SahihConjugator:

    def __init__(self, r1: str, r2: str, r3: str, baab: Baab):
        self.r1, self.r2, self.r3 = r1, r2, r3
        self.baab = baab
        self.vp = _r2_past_v(baab)
        self.vm = _r2_pres_v(baab)

    def _base_past(self) -> str:
        """ر١ + حركة + ر٢ + حركة + ر٣ (ر٣ بلا حركة، الحركة في اللاحقة)"""
        return self.r1 + F + self.r2 + self.vp + self.r3

    def _base_past_pass(self) -> str:
        return self.r1 + D + self.r2 + K + self.r3

    def past_active(self) -> list[tuple]:
        b = self._base_past()
        return [(b + sfx, pgn) for pgn, sfx in PAST_ACT_SFX.items()]

    def past_passive(self) -> list[tuple]:
        b = self._base_past_pass()
        return [(b + sfx, pgn) for pgn, sfx in PAST_PASS_SFX.items()]

    def _present_stem(self) -> str:
        """ر١ + سكون + ر٢ + حركة + ر٣"""
        return self.r1 + S + self.r2 + self.vm + self.r3

    def _present_stem_pass(self) -> str:
        """للمجهول: حرف المضارعة مضموم + ر١ + سكون + ر٢ + فتحة + ر٣"""
        return self.r1 + S + self.r2 + F + self.r3

    def present_active(self, sfx_tbl: dict, mood: str) -> list[tuple]:
        stem = self._present_stem()
        return [(PRES_PREFIX[pgn] + stem + sfx, pgn)
                for pgn, sfx in sfx_tbl.items()]

    def present_passive(self, sfx_tbl: dict) -> list[tuple]:
        stem = self._present_stem_pass()
        results = []
        for pgn, sfx in sfx_tbl.items():
            pre = PRES_PREFIX[pgn]
            # البادئة تُضمّ في المجهول
            form = pre[0] + D + stem + sfx
            results.append((form, pgn))
        return results

    def imperative(self) -> list[tuple]:
        vm = self.vm
        conn = D if vm == D else K   # همزة الوصل: اُفْعُلْ أو اِفْعِلْ/اِفْعَلْ
        vowel_str = "اُ" if conn == D else "اِ"
        base = vowel_str + self.r1 + S + self.r2 + vm + self.r3
        return [(base + sfx, pgn) for pgn, sfx in IMP_SFX.items()]


# ══════════════════════════════════════════════════════════════════════
# المضعَّف — إدغام (ردّ، مدّ، شدّ)
# ══════════════════════════════════════════════════════════════════════

class _MudaafConjugator(_SahihConjugator):
    """ر٢ = ر٣ → إدغام. القاعدة: الإدغام يبقى ما لم يسبق صامت."""

    def past_active(self) -> list[tuple]:
        r1, r2 = self.r1, self.r2
        vp = self.vp
        # القاعدة: ضمائر الغائب (هو/هي/هما) → إدغام (رَدَّ)
        #          ضمائر تبدأ بساكن (هن/خطاب/متكلم) → فك إدغام (رَدَدْتَ)
        base_m = r1 + F + r2 + SH   # رَدَّ (الشدة بدون حركة نهائية)
        base_s = r1 + F + r2 + F + r2  # رَدَدَ (قبل إضافة السكون+اللاحقة)
        results = []
        for pgn, sfx in PAST_ACT_SFX.items():
            if pgn[0] == "غائب" and pgn[1] in ("مفرد", "مثنى"):
                form = base_m + sfx
            elif pgn == ("غائب", "جمع", "مذكر"):
                form = r1 + F + r2 + D + SH + W + A   # رَدُّوا (شدة + ضمة)
            elif pgn == ("غائب", "جمع", "مؤنث"):
                form = base_s + S + "نَ"              # رَدَدْنَ
            else:
                # فك الإدغام: رَدَدْتَ
                form = base_s + sfx                   # sfx يبدأ بسكون
            results.append((form, pgn))
        return results

    def past_passive(self) -> list[tuple]:
        r1, r2 = self.r1, self.r2
        base_m = r1 + D + r2 + SH   # رُدَّ
        base_s = r1 + D + r2 + K + r2  # رُدِدَ
        results = []
        for pgn, sfx in PAST_PASS_SFX.items():
            if pgn[0] == "غائب" and pgn[1] in ("مفرد", "مثنى"):
                form = base_m + sfx
            elif pgn == ("غائب", "جمع", "مذكر"):
                form = r1 + D + r2 + D + SH + W + A   # رُدُّوا
            elif pgn == ("غائب", "جمع", "مؤنث"):
                form = base_s + S + "نَ"
            else:
                form = base_s + sfx
            results.append((form, pgn))
        return results

    def _present_stem(self) -> str:
        # يَرُدُّ: إدغام يُنقل معه الحركة إلى ر١
        # يَرْدُدُ → يَرُدُّ (الضمة انتقلت من الدال الأولى إلى الراء)
        return self.r1 + D + self.r2 + SH

    def imperative(self) -> list[tuple]:
        r1, r2 = self.r1, self.r2
        vm = self.vm   # الحركة المضارعة (D أو K)
        # اُرُدَّ → رُدَّ (المشهور: إدغام مع الفتحة)
        # base_m = الصيغة المدغمة: r1+vm+r2+SH
        base_m = r1 + vm + r2 + SH
        base_s = r1 + S + r2 + vm + r2   # الفك: اُرْدُدْ
        results = []
        for pgn, sfx in IMP_SFX.items():
            if pgn == ("مخاطب", "مفرد", "مذكر"):
                form = "اُ" + base_m + S     # اُرُدَّ/اُرِدَّ
            elif pgn == ("مخاطب", "مفرد", "مؤنث"):
                form = "اُ" + base_m + K + Y  # اُرُدِّي
            elif pgn in [("مخاطب", "مثنى", "مذكر"), ("مخاطب", "مثنى", "مؤنث")]:
                form = "اُ" + base_m + F + A   # اُرُدَّا
            elif pgn == ("مخاطب", "جمع", "مذكر"):
                form = "اُ" + base_m + D + W + A  # اُرُدُّوا
            else:
                form = "اُ" + base_s + S + "نَ"   # اُرْدُدْنَ (فك)
            results.append((form, pgn))
        return results


# ══════════════════════════════════════════════════════════════════════
# المثال الواوي — حذف الواو في المضارع والأمر (وصَلَ → يَصِلُ)
# ══════════════════════════════════════════════════════════════════════

class _MithalWawConjugator(_SahihConjugator):

    def present_active(self, sfx_tbl: dict, mood: str) -> list[tuple]:
        # ر١ (واو) تُحذف في المضارع
        r2, r3 = self.r2, self.r3
        vm = self.vm
        stem = r2 + vm + r3
        return [(PRES_PREFIX[pgn] + stem + sfx, pgn)
                for pgn, sfx in sfx_tbl.items()]

    def present_passive(self, sfx_tbl: dict) -> list[tuple]:
        r2, r3 = self.r2, self.r3
        stem = r2 + F + r3
        results = []
        for pgn, sfx in sfx_tbl.items():
            pre = PRES_PREFIX[pgn]
            form = pre[0] + D + stem + sfx
            results.append((form, pgn))
        return results

    def imperative(self) -> list[tuple]:
        # صِلْ (بدون همزة وصل؛ لأن الحرف الأول متحرك بعد الحذف)
        r2, r3 = self.r2, self.r3
        vm = self.vm
        base = r2 + vm + r3
        return [(base + sfx, pgn) for pgn, sfx in IMP_SFX.items()]


# ══════════════════════════════════════════════════════════════════════
# الأجوف الواوي — قالَ / يقولُ / قُلْ
# ══════════════════════════════════════════════════════════════════════

class _AjwafWawConjugator(_SahihConjugator):
    """
    ر٢ = واو. الإعلال:
    ماضٍ معلوم: قَوَلَ → قَالَ (قلب الواو المتحركة ألفاً)
    مضارع: يَقُولُ (الواو ساكنة = تبقى)
    مجهول ماضٍ: قِيلَ (قلب الواو ياءً في المجهول)
    خطاب/متكلم ماضٍ: قُلْتَ (إعلال بالتسكين + حذف)
    """

    def past_active(self) -> list[tuple]:
        r1, r3 = self.r1, self.r3
        # هو/هما/ها + جمع مذكر: قَالَ
        base_alef = r1 + F + A + r3    # قَال + لاحقة
        # هن: قُلْنَ (حذف ألف + تسكين)
        base_hn   = r1 + D + r3 + S    # قُلْ
        # خطاب/متكلم: قُلْتَ
        base_d    = r1 + D + r3        # قُل (ضمة على ر١ + ر٣ بلا حركة)
        results = []
        for pgn, sfx in PAST_ACT_SFX.items():
            if pgn[0] == "غائب" and pgn[1] in ("مفرد", "مثنى"):
                form = base_alef + sfx
            elif pgn == ("غائب", "جمع", "مذكر"):
                form = base_alef + D + W + A    # قَالُوا
            elif pgn == ("غائب", "جمع", "مؤنث"):
                form = base_hn + "نَ"           # قُلْنَ
            else:
                # sfx يبدأ بـ S للخطاب/المتكلم في الماضي الصحيح
                # هنا ر٣ يحمل الضمة وسكون بدل الفتحة
                form = base_d + sfx             # قُلْتَ (sfx = S+تَ = ْتَ)
            results.append((form, pgn))
        return results

    def past_passive(self) -> list[tuple]:
        r1, r3 = self.r1, self.r3
        # قِيلَ (واو → ياء في المجهول)
        base_yaa  = r1 + K + Y + r3    # قِيل + لاحقة
        base_hn   = r1 + K + r3 + S
        base_d    = r1 + K + r3
        results = []
        for pgn, sfx in PAST_PASS_SFX.items():
            if pgn[0] == "غائب" and pgn[1] in ("مفرد", "مثنى"):
                form = base_yaa + sfx
            elif pgn == ("غائب", "جمع", "مذكر"):
                form = base_yaa + D + W + A
            elif pgn == ("غائب", "جمع", "مؤنث"):
                form = base_hn + "نَ"
            else:
                form = base_d + sfx
            results.append((form, pgn))
        return results

    def _present_stem(self) -> str:
        # يَقُولُ: ر١ + واو ساكنة + ر٣
        r1, r3 = self.r1, self.r3
        vm = self.vm   # DAMMA لهذا النوع
        return r1 + vm + W + r3

    def present_passive(self, sfx_tbl: dict) -> list[tuple]:
        r1, r3 = self.r1, self.r3
        # يُقَالُ
        stem = r1 + F + A + r3
        results = []
        for pgn, sfx in sfx_tbl.items():
            pre = PRES_PREFIX[pgn]
            form = pre[0] + D + stem + sfx
            results.append((form, pgn))
        return results

    def imperative(self) -> list[tuple]:
        r1, r3 = self.r1, self.r3
        vm = self.vm
        # قُلْ (بدون همزة وصل لأن ر١ متحرك)
        base = r1 + vm + r3
        return [(base + sfx, pgn) for pgn, sfx in IMP_SFX.items()]


# ══════════════════════════════════════════════════════════════════════
# الأجوف اليائي — باعَ / يبيعُ / بِعْ
# ══════════════════════════════════════════════════════════════════════

class _AjwafYaaConjugator(_AjwafWawConjugator):
    """ر٢ = ياء. نفس منطق الواوي لكن بالياء."""

    def past_active(self) -> list[tuple]:
        r1, r3 = self.r1, self.r3
        base_alef = r1 + F + A + r3    # بَاع
        base_hn   = r1 + K + r3 + S    # بِعْ  (كسرة لأن الياء)
        base_d    = r1 + K + r3        # بِع
        results = []
        for pgn, sfx in PAST_ACT_SFX.items():
            if pgn[0] == "غائب" and pgn[1] in ("مفرد", "مثنى"):
                form = base_alef + sfx
            elif pgn == ("غائب", "جمع", "مذكر"):
                form = base_alef + D + W + A    # بَاعُوا
            elif pgn == ("غائب", "جمع", "مؤنث"):
                form = base_hn + "نَ"           # بِعْنَ
            else:
                form = base_d + sfx
            results.append((form, pgn))
        return results

    def past_passive(self) -> list[tuple]:
        r1, r3 = self.r1, self.r3
        # بِيعَ
        base_yaa = r1 + K + Y + r3
        base_hn  = r1 + K + r3 + S
        base_d   = r1 + K + r3
        results = []
        for pgn, sfx in PAST_PASS_SFX.items():
            if pgn[0] == "غائب" and pgn[1] in ("مفرد", "مثنى"):
                form = base_yaa + sfx
            elif pgn == ("غائب", "جمع", "مذكر"):
                form = base_yaa + D + W + A
            elif pgn == ("غائب", "جمع", "مؤنث"):
                form = base_hn + "نَ"
            else:
                form = base_d + sfx
            results.append((form, pgn))
        return results

    def _present_stem(self) -> str:
        r1, r3 = self.r1, self.r3
        # يَبِيعُ: ر١ + كسرة + ياء + ر٣
        return r1 + K + Y + r3

    def imperative(self) -> list[tuple]:
        r1, r3 = self.r1, self.r3
        # بِعْ
        base = r1 + K + r3
        return [(base + sfx, pgn) for pgn, sfx in IMP_SFX.items()]


# ══════════════════════════════════════════════════════════════════════
# الناقص اليائي — رَمَى / يَرْمِي / اِرْمِ
# ══════════════════════════════════════════════════════════════════════

class _NaqisConjugator(_SahihConjugator):
    """الناقص (لامه واو أو ياء) بحسب حركة عين الماضي والمضارع — إعادة كتابة 2026-11-06 (تغلق D-M05/D-M06/D-M07
    وعيب الناقص على فَعِلَ). السند: الشذا (باب الناقص)، وشرح الرضي على الشافية (الإعلال بالقلب والحذف).
      الماضي:  فَعَلَ رَمَى/دَعَا، رَمَيْتُ/دَعَوْتُ، رَمَوْا · فَعِلَ بَقِيَ/رَضِيَ، بَقُوا · فَعُلَ سَرُوَ، سَرُوا
      المجهول: رُمِيَ/دُعِيَ، رُمُوا · المضارع: كسر يَرْمِي، ضمّ يَدْعُو، فتح يَبْقَى/يَسْعَى (والمجهول يُرْمَى/يُدْعَى)
      الجزم بحذف حرف العلّة: يَرْمِ، يَدْعُ، يَبْقَ · الأمر: اِرْمِ، اُدْعُ، اِبْقَ"""
    R = Y

    def _past(self, b, v):
        """b = ر١+فتحة/ضمة+ر٢ ، v = حركة العين"""
        R = self.R
        res = []
        for pgn, sfx in PAST_ACT_SFX.items():
            if v == F:                                   # رَمَى، دَعَا
                if pgn == ("غائب", "مفرد", "مذكر"):
                    f = b + F + ("ى" if R == Y else A)
                elif pgn in (("غائب", "مفرد", "مؤنث"), ("غائب", "مثنى", "مؤنث")):
                    f = b + F + sfx[1:]                  # رَمَتْ، رَمَتَا
                elif pgn == ("غائب", "جمع", "مذكر"):
                    f = b + F + W + S + A                # رَمَوْا
                elif pgn == ("غائب", "مثنى", "مذكر"):
                    f = b + F + R + F + A                # رَمَيَا، دَعَوَا
                else:
                    f = b + F + R + sfx                  # رَمَيْتَ، دَعَوْنَ
            else:
                L = Y if v == K else W                   # بَقِيَ/رَضِيَ ، سَرُوَ
                if pgn == ("غائب", "جمع", "مذكر"):
                    f = b + D + W + A                    # بَقُوا، سَرُوا، رُمُوا
                elif sfx.startswith(S):
                    f = b + v + L + sfx                  # بَقِيتَ، بَقِينَ
                else:
                    f = b + v + L + sfx                  # بَقِيَ، بَقِيَتْ، بَقِيَا
            res.append((f, pgn))
        return res

    def past_active(self):
        return self._past(self.r1 + F + self.r2, self.vp)

    def past_passive(self):
        return self._past(self.r1 + D + self.r2, K)

    def _present(self, pre_v, v, tbl):
        """pre_v حركة حرف المضارعة، v حركة العين في المضارع، tbl جدول اللواحق (يُعرف المزاج منه)."""
        st = self.r1 + S + self.r2
        res = []
        for pgn, sfx in tbl.items():
            p = PRES_PREFIX[pgn][0] + pre_v
            if v == F:                                   # يَبْقَى، يُرْمَى
                m = {D: "ى", F: "ى", S: "", F + A + "نِ": Y + F + A + "نِ", F + A: Y + F + A,
                     D + W + "نَ": W + S + "نَ", D + W + A: W + S + A, S + "نَ": Y + S + "نَ",
                     K + Y + "نَ": Y + S + "نَ", K + Y: Y + S}[sfx]
                f = p + st + F + m
            elif v == K:                                 # يَرْمِي
                m = {D: K + Y, F: K + Y + F, S: K, F + A + "نِ": K + Y + F + A + "نِ", F + A: K + Y + F + A,
                     D + W + "نَ": D + W + "نَ", D + W + A: D + W + A, S + "نَ": K + Y + "نَ",
                     K + Y + "نَ": K + Y + "نَ", K + Y: K + Y}[sfx]
                f = p + st + m
            else:                                        # يَدْعُو
                m = {D: D + W, F: D + W + F, S: D, F + A + "نِ": D + W + F + A + "نِ", F + A: D + W + F + A,
                     D + W + "نَ": D + W + "نَ", D + W + A: D + W + A, S + "نَ": D + W + "نَ",
                     K + Y + "نَ": K + Y + "نَ", K + Y: K + Y}[sfx]
                f = p + st + m
            res.append((f, pgn))
        return res

    def present_active(self, sfx_tbl, mood):
        return self._present(F, self.vm, sfx_tbl)

    def present_passive(self, sfx_tbl):
        return self._present(D, F, sfx_tbl)

    def imperative(self):
        v = self.vm
        hw = "اُ" if v == D else "اِ"
        st = hw + self.r1 + S + self.r2
        res = []
        for pgn, sfx in IMP_SFX.items():
            if v == F:
                m = {S: F, K + Y: F + Y + S, F + A: F + Y + F + A, D + W + A: F + W + S + A, S + "نَ": F + Y + S + "نَ"}[sfx]
            elif v == K:
                m = {S: K, K + Y: K + Y, F + A: K + Y + F + A, D + W + A: D + W + A, S + "نَ": K + Y + "نَ"}[sfx]
            else:
                m = {S: D, K + Y: K + Y, F + A: D + W + F + A, D + W + A: D + W + A, S + "نَ": D + W + "نَ"}[sfx]
            res.append((st + m, pgn))
        return res


class _MudaafConjugator2(_SahihConjugator):
    """المضعّف — إعادة كتابة 2026-11-06 (تغلق D-M01/D-M02). يُدغم ما تحرّك ثانيه، ويُفكّ قبل ضمير رفع متحرّك
    أو نون النسوة (رَدَدْتُ، يَرْدُدْنَ)؛ الجزم والأمر للمفرد بالإدغام مفتوحاً (يَرُدَّ، رُدَّ) والفكّ جائز (C5).
    السند: سيبويه (باب ما يُدغم في مثله)، الشذا (المضعّف)."""

    def _past(self, b1, v):
        X = self.r2
        m, s = b1 + X + SH, b1 + X + v + X
        res = []
        for g, sfx in PAST_ACT_SFX.items():
            if g == ("غائب", "جمع", "مذكر"):
                res.append((m + D + W + A, g))
            elif sfx.startswith(S):
                res.append((s + sfx, g))
            else:
                res.append((m + sfx, g))
        return res

    def past_active(self):
        return self._past(self.r1 + F, self.vp)

    def past_passive(self):
        return self._past(self.r1 + D, K)

    def _pres(self, pv, v, tbl, jazm=False):
        X, r1 = self.r2, self.r1
        m, s = r1 + v + X + SH, r1 + S + X + v + X
        res = []
        for g, sfx in tbl.items():
            p = PRES_PREFIX[g][0] + pv
            if sfx == S + "نَ":
                res.append((p + s + sfx, g))
            elif jazm and sfx == S:
                res.append((p + m + F, g))                 # يَرُدَّ
            else:
                res.append((p + m + sfx, g))
        return res

    def present_active(self, tbl, mood):
        return self._pres(F, self.vm, tbl, jazm=(mood == "مجزوم"))

    def present_passive(self, tbl):
        return self._pres(D, F, tbl)

    def imperative(self):
        X, r1, v = self.r2, self.r1, self.vm
        m = r1 + v + X + SH
        hw = "اُ" if v == D else "اِ"
        res = []
        for g, sfx in IMP_SFX.items():
            if sfx == S:
                res.append((m + F, g))                     # رُدَّ
            elif sfx == S + "نَ":
                res.append((hw + r1 + S + X + v + X + sfx, g))   # اُرْدُدْنَ
            else:
                res.append((m + sfx, g))                   # رُدِّي، رُدَّا، رُدُّوا
        return res


class _AjwafConjugator2(_SahihConjugator):
    """الأجوف — إعادة كتابة 2026-11-06 (تغلق D-M04). الماضي والمجهول كما في المصرّفين السابقين؛
    المضارع والأمر: حرف المدّ يُحذف لالتقاء الساكنين (يَقُلْ، يَقُلْنَ، قُلْ، قُلْنَ) ويبقى قبل المتحرّك (قُولِي، يَقُولُوا).
    السند: الشذا (الأجوف)، شرح الرضي (الحذف لالتقاء الساكنين)."""
    _BASE = None

    def __init__(self, r1, r2, r3, baab):
        super().__init__(r1, r2, r3, baab)
        self._old = self._BASE(r1, r2, r3, baab)

    def past_active(self):
        return self._old.past_active()

    def past_passive(self):
        return self._old.past_passive()

    def _madd(self, v):
        return {D: W, K: Y, F: A}[v]

    def _pres(self, pv, v, tbl, jazm=False):
        r1, r3 = self.r1, self.r3
        long, short = r1 + v + self._madd(v) + r3, r1 + v + r3
        res = []
        for g, sfx in tbl.items():
            p = PRES_PREFIX[g][0] + pv
            if sfx == S + "نَ" or (jazm and sfx == S):
                res.append((p + short + sfx, g))
            else:
                res.append((p + long + sfx, g))
        return res

    def present_active(self, tbl, mood):
        return self._pres(F, self.vm, tbl, jazm=(mood == "مجزوم"))

    def present_passive(self, tbl):
        return self._pres(D, F, tbl)

    def imperative(self):
        r1, r3, v = self.r1, self.r3, self.vm
        res = []
        for g, sfx in IMP_SFX.items():
            if sfx in (S, S + "نَ"):
                res.append((r1 + v + r3 + sfx, g))         # قُلْ، قُلْنَ
            else:
                res.append((r1 + v + self._madd(v) + r3 + sfx, g))
        return res


class _AjwafWawConjugator2(_AjwafConjugator2):
    _BASE = _AjwafWawConjugator


class _AjwafYaaConjugator2(_AjwafConjugator2):
    _BASE = _AjwafYaaConjugator


class _MithalWawConjugator2(_MithalWawConjugator):
    """المضارع المجهول يردّ الواو: يُوصَلُ (تغلق D-M03)."""

    # الواو تُحذف في المضارع والأمر إذا كان مكسور العين وحده (يَعِدُ، عِدْ)؛ وتبقى مع الضمّ والفتح
    # (وَضُؤَ يَوْضُؤُ، وَجِلَ يَوْجَلُ) — الشذا، باب المثال
    def present_active(self, sfx_tbl, mood):
        if self.vm == K:
            return super().present_active(sfx_tbl, mood)
        return _SahihConjugator.present_active(self, sfx_tbl, mood)

    def imperative(self):
        if self.vm == K:
            return super().imperative()
        res = []
        for pgn, sfx in IMP_SFX.items():
            hw = "اُ" if self.vm == D else "اِ"
            long = (D + W) if self.vm == D else (K + Y)
            res.append((hw[0] + long + self.r2 + self.vm + self.r3 + sfx, pgn))   # اُوزُنْ، اِيجَلْ
        return res

    def present_passive(self, tbl):
        return [(PRES_PREFIX[g][0] + D + W + self.r2 + F + self.r3 + sfx, g) for g, sfx in tbl.items()]


class _NaqisYaaConjugator(_NaqisConjugator):
    R = Y


class _NaqisWawConjugator(_NaqisConjugator):
    R = W


# ══════════════════════════════════════════════════════════════════════
# اختيار المُصرِّف
# ══════════════════════════════════════════════════════════════════════


def _get_conjugator(letters: str, root_type: RootType, baab: Baab):
    chars = list(letters)
    # fail-closed (D-D09 الرباعي، D-M08 اللفيف، والمهموز): core/support.py
    check_supported(letters, root_type)
    r1, r2, r3 = chars[0], chars[1], chars[2]

    dispatch = {
        RootType.MUDAAF:      _MudaafConjugator2,
        RootType.MITHAL_WAW:  _MithalWawConjugator2,
        RootType.AJWAF_WAW:   _AjwafWawConjugator2,
        RootType.AJWAF_YAA:   _AjwafYaaConjugator2,
        RootType.NAQIS_YAA:   _NaqisYaaConjugator,
        RootType.NAQIS_WAW:   _NaqisWawConjugator,
    }
    cls = dispatch.get(root_type, _SahihConjugator)
    return cls(r1, r2, r3, baab)


def merge_nun(form: str) -> str:
    """لام ساكنة نوناً + نون النسوة أو «نا» تُكتبان نوناً مشدّدة: سَكَنَّ، سَكَنَّا، يَسْكُنَّ، اُسْكُنَّ، كُنَّ
    (قراءة عيّنة الرباعي 2026-11-05: كان المحرك يكتب نْنَ)."""
    for tail in ("نْنَا", "نْنَ"):
        if form.endswith(tail):
            return form[: -len(tail)] + "نّ" + tail[3:]
    return form


def _rasm(f):
    """كلّ وجهٍ من وجوه الخلية (C5 «/») يُرسم بهمزة الوصل ٱ."""
    return "/".join(rasm_wasl(x) for x in f.split("/")) if isinstance(f, str) else f


def _ibtida(f):
    return ibtida(f.split("/")[0]) if isinstance(f, str) else ""


def _cells(pairs: list[tuple], mood: str, voice: str) -> list[ConjugationCell]:
    return [
        ConjugationCell(
            form=_rasm(f), person=pgn[0], number=pgn[1], gender=pgn[2],
            voice=voice, mood=mood, ibtida=_ibtida(f)
        )
        for f, pgn in pairs
    ]


# ══════════════════════════════════════════════════════════════════════
# الدالة العامة
# ══════════════════════════════════════════════════════════════════════

def conjugate(letters: str, root_type: RootType, baab: Baab) -> ConjugationParadigm:
    """
    تُولِّد النموذج الصرفي الكامل للفعل الثلاثي المجرد.

    المدخلات:
        letters   — الحروف الأصلية الثلاثة (كتب / قول / رمي / دعو ...)
        root_type — نوع الجذر
        baab      — الباب الصرفي

    المخرجات:
        ConjugationParadigm ≈ 90 خلية
    """
    p = ConjugationParadigm(root=letters, root_type=root_type, baab=baab)
    c = _get_conjugator(letters, root_type, baab)

    # الماضي
    p.cells += _cells(c.past_active(),  "ماضٍ", "معلوم")
    p.cells += _cells(c.past_passive(), "ماضٍ", "مجهول")

    # المضارع
    p.cells += _cells(c.present_active(PRES_MARFUU, "مرفوع"),  "مضارع مرفوع", "معلوم")
    p.cells += _cells(c.present_passive(PRES_MARFUU),           "مضارع مرفوع", "مجهول")
    p.cells += _cells(c.present_active(PRES_MANSUB, "منصوب"),  "مضارع منصوب", "معلوم")
    p.cells += _cells(c.present_active(PRES_MAJZUM, "مجزوم"),  "مضارع مجزوم", "معلوم")

    # الأمر
    p.cells += _cells(c.imperative(), "أمر", "معلوم")

    if letters[2] == "ن":
        for cell in p.cells:
            cell.form = merge_nun(cell.form)

    return p
