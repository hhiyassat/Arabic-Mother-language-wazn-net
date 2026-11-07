"""
taadiya_engine.py — الحقل الثالث: صلة التعدية (لازم ← أَفْعَلَ/فَعَّلَ، ويكتسب المفعولُ صفةَ اللازم).

السند (من جدول ahdath، توثيق الجلسة الأخرى): سيبويه، باب افتراق فعلت وأفعلت (أخرجه، أدخله، أجلسه)؛ الخليل:
أحزنته = جعلته حزيناً؛ الكفوي: «التعدية بالهمزة قياسية … في القاصر». مانعه: أفعل الذي ليس للتعدية (أسرى، أشرق).

المصدر: ~/arabic-net/Arabic-Mother-language-net/ahdath/taadiya_<route>.tsv (قراءة فقط؛ تبنيه الجلسة الأخرى وتقيسه).
لا يُعرض إلا مسلك قُبل بالقياس (ويلسون الأدنى ≥ 0.78). المسالك المقبولة في ACCEPTED_ROUTES، وتُحدَّث بعد كل قياس.
  2026-11-06: T (taadiya_T_pool، الصيغة وحدها) — 33/53، ويلسون 0.488 → BLOCK، لا يُبنى عليه؛
              T_JAL (نصّ الوسيط «جعله <اللازم>»، 25 زوجاً) — 25/25، ويلسون 0.867 → ACCEPT.
طلب مسلك غير مقبول يُرفض بـ RouteNotAccepted، صراحةً لا تخميناً. CANDIDATE.
"""
from __future__ import annotations
import csv, os, unicodedata
from dataclasses import dataclass
from core.support import rasm_wasl

AHDATH = os.path.expanduser("~/arabic-net/Arabic-Mother-language-net/ahdath")
ROUTE_FILES = {"T": "taadiya_T_pool.tsv", "T_JAL": "taadiya_T_JAL.tsv",
               "T_TAD": "taadiya_T_TAD.tsv"}   # T_TAD (فعّل بنصّ جعله/صيّره) محجوب: 18/28، ويلسون 0.458
ACCEPTED_ROUTES: dict = {"T_JAL": "25/25 wilson 0.867 (ahdath، نصّ الوسيط «جعله <اللازم>»، 2026-11-06)"}


class RouteNotAccepted(LookupError):
    """المسلك لم يجتز القياس — لا يُعرض."""


class NoSamaa(LookupError):
    """لا زوج تعدية مسموع لهذا الفعل في المسالك المقبولة."""


@dataclass(frozen=True)
class Taadiya:
    lazim: str            # حَزِنَ
    mutaaddi: str         # أَحْزَنَ
    form: str
    sifa: str             # صفة اللازم التي يكتسبها المفعول: حَزِين
    sifa_kind: str
    maful: str            # مُحْزَن
    route: str
    measure: str
    rank: str = "CANDIDATE"


def _k(v):
    return unicodedata.normalize("NFC", v or "").replace("ْ", "").strip().replace("ٱ", "ا")


def _rows(route):
    p = os.path.join(AHDATH, ROUTE_FILES[route])
    if not os.path.exists(p):
        return []
    return list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))


def taadiya_of(lazim: str, routes=None) -> list[Taadiya]:
    """اللازم → أزواج التعدية من المسالك المقبولة وحدها."""
    routes = list(routes or ROUTE_FILES)
    bad = [r for r in routes if r not in ACCEPTED_ROUTES]
    if len(bad) == len(routes):
        raise RouteNotAccepted(f"لا مسلك مقبول بالقياس بين {routes} (المقبول: {sorted(ACCEPTED_ROUTES) or 'لا شيء'})")
    out = []
    for route in routes:
        if route not in ACCEPTED_ROUTES:
            continue
        for r in _rows(route):
            if _k(r.get("base")) == _k(lazim):
                out.append(Taadiya(rasm_wasl(r["base"]), rasm_wasl(r["verb"]), r["form"], r.get("sifa", ""), r.get("sifa_kind", ""),
                                   r.get("maful", ""), route, ACCEPTED_ROUTES[route]))
    if not out:
        raise NoSamaa(f"لا زوج تعدية مسموعاً للفعل {lazim!r} في {sorted(ACCEPTED_ROUTES)}")
    return out
