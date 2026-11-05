"""الحقل الثاني: المطاوعة فعلاً بفعل من المسموع (خطة الحقول الخمسة). القيم مضمَّنة، OWNER_RATIFIED=NO."""
import csv
import pytest

from engines.mutawaa_engine import mutawaa_of, base_of, NoSamaa, TABLE


@pytest.mark.parametrize("base,mut,athar", [
    ("كَسَرَ", "انْكَسَرَ", "انْكِسَار"),
    ("حَرَّكَ", "تَحَرَّكَ", "تَحَرُّك"),
    ("رَزَقَ", "ارْتَزَقَ", "ارْتِزَاق"),
    ("أَفْرَحَ", "فَرِحَ", "فَرَح"),
    ("عَطَفَ", "انْعَطَفَ", "انْعِطَاف"),
])
def test_known_pairs(base, mut, athar):
    got = {(m.mutawaa, m.athar) for m in mutawaa_of(base)}
    assert (mut, athar) in got
    assert base in {m.base for m in base_of(mut)}


def test_sukun_optional_in_lookup():
    assert mutawaa_of("كَسَرَ") == mutawaa_of("كَسَرَ ")


@pytest.mark.parametrize("verb", ["اكْتَسَبَ", "كَتَبَ", "غير_فعل"])
def test_not_heard_is_rejected(verb):
    """ليس كل افتعل مطاوعاً: اكْتَسَبَ لا مطاوَع له في الجدول، فيُرفض ولا يُخمَّن."""
    with pytest.raises(NoSamaa):
        base_of(verb) if verb.startswith("ا") else mutawaa_of(verb)


def test_table_integrity():
    rows = list(csv.DictReader(open(TABLE, encoding="utf-8"), delimiter="\t"))
    assert rows and all(r["rank"] == "CANDIDATE" for r in rows)
    assert all(r["route"] for r in rows) and all(r["base"] != r["mutawaa"] for r in rows)
    assert len({(r["base"], r["mutawaa"]) for r in rows}) == len(rows)
    # تَفَعَّلَ لا يُقرن بفَعَلَ في مسلك العبارة (قراءة العيّنة)
    assert not [r for r in rows if r["route"] == "LEX_FORMULA" and r["mutawaa_form"].startswith("تَفَعَّلَ")
                and r["base_form"].split(" ")[0] == "فَعَلَ"]
