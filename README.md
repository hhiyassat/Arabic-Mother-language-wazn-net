# Arabic Mother Language — Wazn & Mushtaqqat
# الأوزان والمشتقات العربية

محركات **الاشتقاق والصرف العربي** المبنية على مقاييس اللغة لابن فارس.  
تُولِّد المشتقات الكاملة للجذر الثلاثي: مصدر، اسم فاعل، اسم مفعول، أوزان II–X.

---

## المتطلبات

- Python 3.9+

---

## المحركات

| الملف | الوصف |
|---|---|
| `engines/derivation_engine.py` | المحرك الاشتقاقي — يولِّد كامل المشتقات |
| `engines/morphological_engine.py` | المحرك الصرفي — يصرِّف الفعل في جميع الأزمنة |
| `engines/slots_engine.py` | محرك الفتحات الدلالية |
| `engines/compatibility_engine.py` | محرك التوافق بين المشتقات |
| `data/arabic_verb_tree.xlsx` | شجرة الأفعال العربية مع الجذور |
| `wazn_constitution_2.html` | دستور الأوزان — افتحه في المتصفح |

---

## API — المحرك الاشتقاقي

### الاستيراد

```python
from engines.derivation_engine import derive, derive_from_dict, DerivationSet
from core.types import RootType, Baab
```

### توليد مشتقات جذر

```python
from engines.derivation_engine import derive
from core.types import RootType, Baab

ds = derive(
    letters          = "كتب",
    root_type        = RootType.SAHIH,     # صحيح
    baab             = Baab.NASARA,        # باب نصر
    masadir_samiyya  = ["كِتاب", "كتابة"],  # مصادر سماعية
    masdar_qiyasi    = None,
    ism_faail_stored = None,               # يُولَّد تلقائياً
    ism_mafuul_stored= None,
    ism_makan_stored = None,
    ism_zaman_stored = None,
    ism_aala_stored  = None,
    awzaan_maqbuula  = {                   # الأوزان المزيدة المقبولة
        "II":  "للتعدية",
        "IV":  "للإزالة",
        "X":   "للطلب",
    },
)

print(ds.ism_faail)   # كاتب
print(ds.ism_mafuul)  # مكتوب
print(ds.ism_makan)   # مكتب

for m in ds.mazidaat:
    print(m.wazn, m.verb, m.masdar, m.ism_faail, "—", m.meaning)
# II   كتَّب   تكتيب  مكتِّب  — للتعدية
# IV   أكتب   إكتاب  مُكتِب  — للإزالة
# X    استكتب  استكتاب مستكتِب — للطلب
```

### `DerivationSet` — حقول المخرج

| الحقل | الوصف |
|---|---|
| `root` | الجذر |
| `root_type` | نوع الجذر (صحيح / مثال / أجوف / ناقص / مضاعف) |
| `baab` | الباب الصرفي |
| `masadir_samiyya` | المصادر السماعية |
| `masdar_qiyasi` | المصدر القياسي |
| `ism_faail` | اسم الفاعل |
| `ism_mafuul` | اسم المفعول |
| `ism_makan` | اسم المكان |
| `ism_zaman` | اسم الزمان |
| `ism_aala` | اسم الآلة |
| `mazidaat` | قائمة `MazidEntry` للأوزان II–X |

### `MazidEntry` — حقول المزيد

| الحقل | الوصف |
|---|---|
| `wazn` | الوزن: "II"، "III"، ... "X" |
| `verb` | صيغة الفعل الماضي |
| `masdar` | المصدر القياسي |
| `ism_faail` | اسم الفاعل |
| `ism_mafuul` | اسم المفعول |
| `meaning` | الدلالة من الوزن |
| `wazn_op` | العملية الدلالية (+سببية، +ثنائية، ...) |

### الواجهة المُيسَّرة — من قاموس JSON

```python
from engines.derivation_engine import derive_from_dict

root_data = {
    "letters": "علم",
    "root_type": "SAHIH",
    "baab": "NASARA",
    "masadir_samiyya": ["عِلم", "عَلَم"],
    "awzaan_maqbuula": {"II": "للتعليم", "V": "للتفعُّل"}
}

ds = derive_from_dict(root_data)
```

---

## API — المحرك الصرفي

```python
from engines.morphological_engine import conjugate

table = conjugate(
    root      = "كتب",
    root_type = RootType.SAHIH,
    baab      = Baab.NASARA,
)

for cell in table.cells:
    print(cell.mood, cell.person, cell.number, cell.gender, "→", cell.form)
# ماضٍ   غائب   مفرد   مذكر  → كَتَبَ
# ماضٍ   غائب   مفرد   مؤنث  → كَتَبَت
# مضارع  مخاطب  جمع    مذكر  → تَكْتُبُون
# ...
```

`ConjugationCell` يحتوي: `form`، `person`، `number`، `gender`، `voice`، `mood`، `rule`.

---

## API — محرك الفتحات الدلالية

```python
from engines.slots_engine import SlotFrame

frame = SlotFrame.load("علم")

for slot in frame.slots:
    print(slot.name, slot.sem_type, "اختياري" if slot.optional else "إلزامي")
# فاعل   HUMAN    إلزامي
# مفعول  THING    إلزامي
# في      PLACE    اختياري
```

---

## أنواع الجذور — `RootType`

| القيمة | النوع |
|---|---|
| `SAHIH` | صحيح |
| `MITHAL` | مثال (أول حرف علة) |
| `AJWAF` | أجوف (وسط حرف علة) |
| `NAQIS` | ناقص (آخر حرف علة) |
| `MUDAAF` | مضاعف (حرفان متماثلان) |

## أبواب الفعل — `Baab`

| القيمة | مثال |
|---|---|
| `NASARA` | نَصَرَ يَنصُر |
| `DARABA` | ضَرَبَ يَضرِب |
| `FATAHA` | فَتَحَ يَفتَح |
| `HASIBA` | حَسِبَ يَحسَب |
| `KARUMA` | كَرُمَ يَكرُم |
| `FASILA` | فَسِلَ يَفسَل |

---

## البيانات

| الملف | الوصف |
|---|---|
| `data/arabic_verb_tree.xlsx` | شجرة الأفعال الكاملة مع الجذور والأوزان |
| `data/arabic_verb_tree_simple.xlsx` | نسخة مُبسَّطة |
| `data/arabic_verb_tree_with_roots.xlsx` | مع الجذور المُتحقَّق منها من المقاييس |

---

## المصدر

يعتمد هذا المشروع على **مقاييس اللغة** لابن فارس (ت 395هـ) كمرجع للأوزان المقبولة.  
للاستخدام الأكاديمي البحثي فقط.
