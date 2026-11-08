"""
mutawaa_engine.py — الحقل الثاني: صلة الفعل بمطاوعه، فعلاً بفعل من المسموع.

لا يُستنتج المطاوع من الوزن: ليس كل انْفَعَلَ ولا افْتَعَلَ مطاوعاً (اكْتَسَبَ ليس مطاوعاً لشيء).
المصدر: data/mutawaa.tsv (scripts/build_mutawaa.py). ما ليس في الجدول يُرفض بـ NoSamaa، لا يُخمَّن.
الشرط في المطاوعة «علاج وتأثير» (الكفوي، الكليات 27626–27627؛ كشف الأسرار 9670).

القياس (2026-11-05):
  R1_QABILIYYAT  0.964 (gold_R1_MUTAWAA، qabiliyyat)
  LEX_FORMULA    56/59 = 0.949، ويلسون الأدنى 0.861 (عيّنة 60 ببذرة 20261105، قارئ مستقل من Claude)؛
                 الأخطاء الثلاثة (شدّة فَعَّلَ) أُصلحت في البناء.
  R1W_WASIT      «X: مطاوع Yه» في الوسيط (ahdath R1W v2، صيغة الأصل من شكل النصّ): 0.930، ويلسون 0.833 (2026-11-06؛ v1 كان 0.795). الأصل يُقبل إذا وافق وزنُه وزنَ المطاوع؛
                 وإلا base فارغ وbase_status=BASE_UNRESOLVED (يُعرف من base_of بنصّ الوسيط في evidence، ولا يظهر في mutawaa_of).
كل مخرَج CANDIDATE حتى يحكم DR_HUSSEIN.
"""
from __future__ import annotations
import csv, os, re, unicodedata
from dataclasses import dataclass
from core.support import rasm_wasl

TABLE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "mutawaa_v7.tsv")   # v7: v6 + خمسة تفعلل من HFN v47 وتصحيح تمخلّف=تخلّف (v6 محفوظ)
_SUKUN = re.compile("ْ")


class NoSamaa(LookupError):
    """لا مسموع لهذا الفعل في جدول المطاوعة — يُرفض ولا يُخمَّن."""


@dataclass(frozen=True)
class Mutawaa:
    root: str
    base: str            # الفعل المؤثِّر: كَسَرَ
    base_form: str
    mutawaa: str         # المطاوع: انْكَسَرَ
    mutawaa_form: str
    athar: str           # مصدر المطاوع = اسم الأثر: انْكِسَار ("" إن لم يُعرف)
    route: str           # R1_QABILIYYAT / LEX_FORMULA / كلاهما
    n_lex: int
    lexicons: str
    evidence: str
    rank: str = "CANDIDATE"


def _key(verb: str) -> str:
    """مفتاح المطابقة: NFC، والسكون اختياري (C2)، ورسم الهمزة على حاله."""
    return _SUKUN.sub("", unicodedata.normalize("NFC", verb.strip())).replace("ٱ", "ا")   # همزة الوصل: ٱ = ا للمطابقة


_by_base: dict = {}
_by_mut: dict = {}


def _load():
    if _by_base:
        return
    for r in csv.DictReader(open(TABLE, encoding="utf-8"), delimiter="\t"):
        m = Mutawaa(r["root"], rasm_wasl(r["base"]), r["base_form"], rasm_wasl(r["mutawaa"]), r["mutawaa_form"], rasm_wasl(r["athar"]),   # ٱ برسم المصحف (حكم المالك 2026-11-07)؛ الجدول على حاله
                    r["route"], int(r["n_lex"] or 0), r["lexicons"], r["evidence"], r["rank"])
        if m.base:
            _by_base.setdefault(_key(m.base), []).append(m)
        _by_mut.setdefault(_key(m.mutawaa), []).append(m)


def mutawaa_of(verb: str) -> list[Mutawaa]:
    """كَسَرَ → [انْكَسَرَ / انْكِسَار]. يرفع NoSamaa إن لم يُسمع له مطاوع."""
    _load()
    out = _by_base.get(_key(verb))
    if not out:
        raise NoSamaa(f"لا مطاوع مسموعاً للفعل {verb!r} في {os.path.basename(TABLE)}")
    return list(out)


def base_of(verb: str) -> list[Mutawaa]:
    """انْكَسَرَ → [كَسَرَ]. يرفع NoSamaa إن لم يكن الفعل مطاوعاً مسموعاً."""
    _load()
    out = _by_mut.get(_key(verb))
    if not out:
        raise NoSamaa(f"الفعل {verb!r} ليس مطاوعاً مسموعاً في {os.path.basename(TABLE)}")
    return list(out)
