"""known_defects.py — سجلّ عيوب المحرك المعروفة (مقيسة، مصنَّفة يدوياً).

كل حالة هنا تُعلَّم xfail(strict=True): إن أُصلح المحرك صارت XPASS فيفشل التشغيل
حتى تُحذف من السجل. لا يُضاف هنا إلا عيبٌ في المحرك، لا خطأ في القيمة الذهبية.
"""
import pytest

DEFECT_CLASSES = {
    "D-D01": "مصدر فاعَلَ: ما قبل التاء المربوطة بلا فتحة + تنوين خارج الاصطلاح (مُكَاتَبةٌ)",
    "D-D02": "مضعّف: لا إدغام في اسم المكان/الآلة والمزيد (مَرْدَد، اِسْتَرْدَدَ)",
    "D-D03": "مثال واوي: لا قلب للواو ياءً بعد كسرة (مِوْصَل، اِسْتِوْصَال)",
    "D-D04": "أجوف: لا إعلال في اسم المكان (مَقْوَل، مَبْيِع)",
    "D-D05": "أجوف VIII: مصدر بلا فتحة على الياء (اِبْتِياع)",
    "D-D06": "ناقص: اسم المكان على مَفْعِل بحسب الباب، والناقص مَفْعَل دائماً (مَرْمِى)",
    "D-D07": "ناقص: اسم الفاعل ومصدر تَفَعُّل/تَفَاعُل لا يُعَلّان منقوصاً (مُرَمِّي، تَرَمُّي، مُدَعِّو)",
    "D-D08": "ناقص واوي VIII: لا إبدال لتاء الافتعال بعد الدال ولا همزة متطرفة (اِدْتَعَى، اِدْتِعَاو)",
    "D-C01": "م٣ + المحظور ١: محرك التوافق يعطي درجة احتمالية [0..1] لا حكماً ثنائياً",
}

# قائمة مغلقة مقيسة — كل مدخل صُنِّف يدوياً بعد مقارنة المحرك بالذهبي
DEFECTS_BY_CASE = {
    "P3-binary-verdict": "D-C01",
    "بيع-III.masdar": "D-D01",
    "دعو-III.masdar": "D-D01",
    "رمي-III.masdar": "D-D01",
    "قول-III.masdar": "D-D01",
    "كتب-III.masdar": "D-D01",
    "وصل-III.masdar": "D-D01",
    "ردد-I.aala": "D-D02",
    "ردد-I.makan": "D-D02",
    "ردد-I.zaman": "D-D02",
    "ردد-X.faail": "D-D02",
    "ردد-X.mafuul": "D-D02",
    "ردد-X.verb": "D-D02",
    "وصل-I.aala": "D-D03",
    "وصل-X.masdar": "D-D03",
    "بيع-I.makan": "D-D04",
    "بيع-I.zaman": "D-D04",
    "قول-I.makan": "D-D04",
    "قول-I.zaman": "D-D04",
    "بيع-VIII.masdar": "D-D05",
    "رمي-I.makan": "D-D06",
    "رمي-I.zaman": "D-D06",
    "دعو-II.faail": "D-D07",
    "دعو-III.faail": "D-D07",
    "دعو-V.faail": "D-D07",
    "دعو-V.masdar": "D-D07",
    "دعو-VI.faail": "D-D07",
    "دعو-VI.masdar": "D-D07",
    "رمي-II.faail": "D-D07",
    "رمي-III.faail": "D-D07",
    "رمي-V.faail": "D-D07",
    "رمي-V.masdar": "D-D07",
    "رمي-VI.faail": "D-D07",
    "رمي-VI.masdar": "D-D07",
    "دعو-VIII.faail": "D-D08",
    "دعو-VIII.mafuul": "D-D08",
    "دعو-VIII.masdar": "D-D08",
    "دعو-VIII.verb": "D-D08",
    "ورث-I.aala": "D-D03",
}

DEFECTS = {k: f"{c}: {DEFECT_CLASSES[c]}" for k, c in DEFECTS_BY_CASE.items()}


def param(case_id, *values):
    reason = DEFECTS.get(case_id)
    marks = [pytest.mark.xfail(strict=True, reason=reason)] if reason else []
    return pytest.param(*values, id=case_id, marks=marks)
