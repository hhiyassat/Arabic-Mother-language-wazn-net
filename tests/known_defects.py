"""known_defects.py — سجلّ عيوب المحرك المعروفة (مقيسة، مصنَّفة يدوياً).

كل حالة هنا تُعلَّم xfail(strict=True): إن أُصلح المحرك صارت XPASS فيفشل التشغيل
حتى تُحذف من السجل. لا يُضاف هنا إلا عيبٌ في المحرك، لا خطأ في القيمة الذهبية.
"""
import pytest

DEFECT_CLASSES = {
}

# قائمة مغلقة مقيسة — كل مدخل صُنِّف يدوياً بعد مقارنة المحرك بالذهبي
DEFECTS_BY_CASE = {
}

DEFECTS = {k: f"{c}: {DEFECT_CLASSES[c]}" for k, c in DEFECTS_BY_CASE.items()}


def param(case_id, *values):
    reason = DEFECTS.get(case_id)
    marks = [pytest.mark.xfail(strict=True, reason=reason)] if reason else []
    return pytest.param(*values, id=case_id, marks=marks)
