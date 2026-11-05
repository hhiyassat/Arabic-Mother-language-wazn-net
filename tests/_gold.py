"""_gold.py — قراءة الملفات الذهبية وقواعد المقارنة (انظر gold/GOLD_CONVENTIONS.md)."""
import os
import re
import unicodedata

GOLD_DIR = os.path.join(os.path.dirname(__file__), "gold")

# ترتيب الخلايا — مطابق لمفاتيح المحرك (person, number, gender)
PGN14 = [
    ("غائب", "مفرد", "مذكر"), ("غائب", "مفرد", "مؤنث"),
    ("غائب", "مثنى", "مذكر"), ("غائب", "مثنى", "مؤنث"),
    ("غائب", "جمع", "مذكر"), ("غائب", "جمع", "مؤنث"),
    ("مخاطب", "مفرد", "مذكر"), ("مخاطب", "مفرد", "مؤنث"),
    ("مخاطب", "مثنى", "مذكر"), ("مخاطب", "مثنى", "مؤنث"),
    ("مخاطب", "جمع", "مذكر"), ("مخاطب", "جمع", "مؤنث"),
    ("متكلم", "مفرد", "-"), ("متكلم", "جمع", "-"),
]
PGN_IMP = PGN14[6:12]

TABLES = {
    "PA": ("ماضٍ", "معلوم"),
    "PP": ("ماضٍ", "مجهول"),
    "RA": ("مضارع مرفوع", "معلوم"),
    "RP": ("مضارع مرفوع", "مجهول"),
    "NS": ("مضارع منصوب", "معلوم"),
    "JZ": ("مضارع مجزوم", "معلوم"),
    "AM": ("أمر", "معلوم"),
}

PERSON_TAG = ["هو", "هي", "هما_م", "هما_ف", "هم", "هن", "أنتَ", "أنتِ",
              "أنتما_م", "أنتما_ف", "أنتم", "أنتن", "أنا", "نحن"]
IMP_TAG = PERSON_TAG[6:12]

SUKUN = "ْ"
# C2: السكون على حرف المدّ اختياري (و بعد ضمة، ي بعد كسرة، ا)
_MADD_SUKUN = re.compile("(ُو|ِي|ا)ْ")


def norm(s: str) -> str:
    """C1 الصورة القانونية NFC (تُعيد ترتيب الشدة/الحركة) + C2 إسقاط سكون المدّ."""
    s = unicodedata.normalize("NFC", s or "")
    return _MADD_SUKUN.sub(r"\1", s)


def matches(actual: str, alternatives) -> bool:
    a = norm(actual)
    return any(a == norm(g) for g in alternatives)


def _rows(name):
    with open(os.path.join(GOLD_DIR, name), encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            yield line.split("|")


def conjugation_cases():
    """[(case_id, root, table_code, pgn, alternatives)]"""
    out = []
    for root, table, cells in _rows("conjugation_gold.txt"):
        forms = cells.split(",")
        pgns, tags = (PGN_IMP, IMP_TAG) if table == "AM" else (PGN14, PERSON_TAG)
        assert len(forms) == len(pgns), (root, table, len(forms))
        for pgn, tag, f in zip(pgns, tags, forms):
            out.append((f"{root}-{table}-{tag}", root, table, pgn, f.split("/")))
    return out


def derivation_cases():
    """[(case_id, root, key, alternatives)]"""
    return [(f"{r}-{k}", r, k, v.split("/")) for r, k, v in _rows("derivation_gold.txt")]


# علامات الحركة (دون الشدة): فتحتان..سكون
_VOWELS = "ًٌٍَُِْ"


def stacked_vowels(form: str) -> bool:
    """أكثر من علامة حركة على حرف واحد (الشدة مستثناة)."""
    s = unicodedata.normalize("NFD", form)
    n = 0
    for ch in s:
        if ch in _VOWELS:
            n += 1
            if n > 1:
                return True
        elif ch == "ّ":
            continue
        else:
            n = 0
    return False
