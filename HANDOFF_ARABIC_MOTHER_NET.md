# HANDOFF — Arabic Mother Language · Wazn & Mushtaqqat (arabic-mother-net)

RULE_OWNER = DR_HUSSEIN · كُتب 2026-10-06 · الحالة مقيسة من تشغيل فعلي في هذا التاريخ.
المالك يشرّع؛ الوكيل ينفّذ ويقيس. اقرأ هذا الملف كاملاً ثم `wazn_constitution_2.html` قبل أي تعديل.

---

## 0. الحكم الدستوري (يسري على كل عمل هنا)

- كل قرار يُوزن بـ **السبب / الشرط / المانع** → ACCEPT / DEFER / BLOCK. DEFER ≠ BLOCK.
- فجوة قواعد → **STOP / OWNER_ALERT / NO_INFERENCE**: لا قاعدة جديدة، لا استثناء، لا اختيار بين بدائل.
- **MEASURED_NOT_PRESET**؛ اذكر ما لم يُنجز صراحةً.
- لا `FULL_TESTS_PASS=YES` مع أي إخفاق؛ افصل نطاق الجولة عن الشجرة كلها
  (`<ROUND>_SCOPE_TESTS_PASS`, `FULL_TREE_HAS_PRE_EXISTING_OUT_OF_SCOPE_FAILURES`, `<ROUND>_CAUSED_FAILURES`).

### دستور المشروع — `wazn_constitution_2.html` (الإصدار ١٫٠، ١٠ أغسطس ٢٠٢٦، وثيقة مقفلة)
لا يُعدَّل بند منه إلا بإجراء التعديل الدستوري (اقتراح صريح → حوار → موافقة الطرفين صراحةً → توثيق برقم وتاريخ). أهم ما يحكم الوكيل:

1. **الجذر = معنى أصلي واحد** (منهج ابن فارس في «مقاييس اللغة»).
2. **الوزن = محوِّل للخانات (Slots)**، بست عمليات: +سببية · +ثنائية · +انعكاسية · +طلبية · −أثر فاعلي · +حالة ثابتة.
3. **القابلية شرط نوعي (type check) لا احتمال**: عدم التوافق خطأ، لا «معنى ضعيف».
4. **المعنى الأصلي رباعي الطبقات**: تراثي (ابن فارس) · حاسوبي (محمول بنيوي) · صرفي (ملف السلوك) · شبكي (روابط).
5. **«إن أمكن توليده فلا تخزّنه»**: لا يُخزَّن إلا السماعي.
6. أنواع دلالية **15** ومحمولات أولية **20** (`core/types.py`) — قائمة مغلقة.

**المحظورات المطلقة:** لا نماذج احتمالية لتحديد المعنى أو القابلية · **لا يُستورد محتوى الأنواع الدلالية من WordNet أو FrameNet** · لا أكثر من معنى أصلي للجذر · لا حسم للاشتراك اللفظي بالإحصاء · لا يُولَّد المخزَّن ولا يُخزَّن المولَّد · لا تعديل للدستور ضمناً.

---

## 1. الموقع والحالة

```
REPO = /Users/husseinhiyassat/arabic-net/Arabic-Mother-language-wazn-net
HEAD = 6198805a1b64fac3c6284b95e2a0c97ef8613cc0  "Initial commit — Arabic Wazn & Mushtaqqat engines" (2026-08-12)
غير مُودَع (working tree):
  M  tests/test_{compatibility,derivation,morphological,slots}_engine.py   (+203 / −319)
  ?? tests/_gold.py tests/_pilot.py tests/conftest.py tests/known_defects.py tests/gold/{GOLD_CONVENTIONS.md,derivation_gold.txt,conjugation_gold.txt}
  ?? pytest.ini
  ?? data/abniya_sibawayh.csv data/awzaan_af3aal_all.csv data/awzaan_maqbuula.csv data/pilot_roots.json data/sibawayh_abniya_raw/
```
- لا تُودِع (commit) ولا تدفع (push) إلا بطلب المالك. بيانات المالك لا تُعدَّل.
- لا يوجد pytest على Python النظام في جهاز المالك؛ ثبّته في بيئة افتراضية أو شغّل في بيئة أخرى.

### الاختبارات (مقيس 2026-10-06)
```
python3 -m pytest -q -p no:cacheprovider      # من جذر المستودع
→ 1920 passed, 209 xfailed  (xfail_strict = true)
```
- `tests/known_defects.py` **قائمة مغلقة** لعيوب المحرك، كل مدخل `xfail(strict=True)`: إن أُصلح العيب صار XPASS ففشل التشغيل → احذف المدخل. لا يُضاف إليها خطأ في الذهبي، فقط عيب في المحرك.
- `tests/gold/` قيم ذهبية: `OWNER_RATIFIED = NO` (تأليف كلود 2026-10-05). اصطلاحات المقارنة C1–C5 في `tests/gold/GOLD_CONVENTIONS.md` (NFC؛ سكون حرف المد اختياري؛ همزة الوصل ألف بحركة البدء؛ لا علامة إعراب إلا تنوين المنقوص؛ البدائل بـ `/`).
- المختبَر **الشكل لا الترخيص** (`LICENSING_NOT_TESTED`).

### فئات العيوب المعروفة (21)
| النطاق | الرموز |
|---|---|
| المحرك الصرفي (التصريف) | D-M01…D-M08 — مضعّف، مثال واوي، أجوف، ناقص؛ **D-M08 fail-open: اللفيف يُصرَّف صامتاً كالصحيح** |
| المحرك الاشتقاقي | D-D01…D-D10 — مصدر فاعَلَ، إدغام المضعّف، إعلال المثال والأجوف والناقص، إبدال تاء الافتعال؛ **D-D09 fail-open: الرباعي يُقطع إلى ثلاثة أحرف بصمت؛ D-D10 مفتاح وزن مجهول يُسقط بصمت** |
| محرك الخانات | D-S01, D-S02 — مطابقة جزئية في `_resolve_sem_type` / `_resolve_predicate` (مخالفة لا-استنتاج) |
| محرك التوافق | **D-C01 — يعطي درجة احتمالية [0..1] لا حكماً ثنائياً (يخالف المبدأ ٣ والمحظور ١)** |

لا تعتمد على مخرَج يمرّ عبر عيب fail-open (D-M08, D-D09, D-D10) دون فحص صريح للمدخل.

---

## 2. الواجهة البرمجية (متحقَّق منها من الشيفرة — README قديم)

> ⚠️ `README.md` لا يطابق الشيفرة: أسماء الأبواب فيه (`NASARA`, `DARABA`…) غير موجودة، و`SlotFrame.load` غير موجودة، وقيم `RootType` مختلفة. اعتمد ما يلي.

```python
import json
from core.types import RootType, Baab, SemanticType, PrimaryPredicate, WaznOperation
from engines.derivation_engine import derive, derive_from_dict, DerivationSet, MazidEntry
from engines.morphological_engine import conjugate, ConjugationParadigm
from engines.slots_engine import parse_predicate_from_dict, find_compatible_pairs, group_by_predicate, group_by_signature
from engines.compatibility_engine import build_compatibility_map_from_file, check_compatibility

roots = json.load(open("data/pilot_roots.json", encoding="utf-8"))["roots"]   # 10 جذور
r = roots[0]                                   # كتب — مفاتيح: letters, display, root_type, ibn_faris, predicate, morph, network, compatibility_exceptions
ds = derive_from_dict(r)                       # ds.ism_faail='كَاتِب' ds.ism_mafuul='مَكْتُوب' ds.mazidaat=[MazidEntry(wazn,verb,masdar,ism_faail,ism_mafuul,meaning,wazn_op)…]
pred = parse_predicate_from_dict(r)            # pred.summary() → "[صنع] فاعل:مُنجِز مفعول:موضوع في/في:أداة? بـ/بـ:أداة?"
cmap = build_compatibility_map_from_file("data/pilot_roots.json")   # cmap.top_pairs(n) / compatible_with(root) — درجات احتمالية (D-C01)
para = conjugate("كتب", RootType("صحيح"), Baab.FAA_YAF_U)          # ≈ 90 خلية: form, person, number, gender, voice, mood, rule
```

- `RootType` (القيم): صحيح · مضعَّف · مثال واوي · مثال يائي · أجوف واوي · أجوف يائي · ناقص واوي · ناقص يائي · لفيف مقرون · لفيف مفروق.
- `Baab` (الأسماء): `FAA_YAF_U` فَعَلَ يَفْعُلُ · `FAA_YAF_I` فَعَلَ يَفْعِلُ · `FAA_YAF_A` فَعَلَ يَفْعَلُ · `FAI_YAF_A` فَعِلَ يَفْعَلُ · `FAU_YAF_U` فَعُلَ يَفْعُلُ.
  ⚠️ الـ docstring يقول «الأبواب الستة» والمعرَّف خمسة فقط: **باب فَعِلَ يَفْعِلُ (حَسِبَ يَحْسِبُ) غير موجود** → STOP / OWNER_ALERT إن احتاجه جذر.
- `derive` و`conjugate` ترفعان `ValueError` لغير الثلاثي (لكن انظر D-D09 في مسارات أخرى).
- الأوزان المزيدة المولَّدة = `awzaan_maqbuula` للجذر فقط (II–X بأسماء رومانية).
- الباب المعتمد هو **المعلَن في pilot_roots.json** (عقد المحرك)، لا الباب المعجمي (مثال: `حكم` معلَن فَعَلَ يَفْعِلُ).

---

## 3. البيانات (`data/`)

| الملف | المحتوى | الحالة |
|---|---|---|
| `pilot_roots.json` | 10 جذور تجريبية تغطي أنواع الجذور؛ لكل جذر الطبقات الأربع | sha256 `e7e0b42c0a04…` (مثبَّتة في الذهبي) — بيانات المالك |
| `awzaan_maqbuula.csv` | 8 أوزان مزيدة (II…X) مع العملية الدستورية والجذور التجريبية | sha `40c26ab7764a` |
| `awzaan_af3aal_all.csv` | 37 وزناً فعلياً (31 صيغة مختلفة) بمعانيها ومصادرها (الشذا، سيبويه، الرضي) | sha `ba0aee787f99` · `owner_ratified=NO` في الملف، **لكن المالك اعتمده مخزوناً للأفعال في Arabic FrameNet (OWNER_DECISION_L2_001)** |
| `abniya_sibawayh.csv` | 419 بناءً من الكتاب ج4 ص242–303 (EXISTS 214 · RARE 109 · NOT_FOUND_IN_ARABIC 96) | sha `a1c1f7f94378` = نفس `awzan-sibawayh-308.csv` في taaqol · `owner_ratified=NO`؛ مستخرج آلياً من الشاملة (غير مضبوط في المصدر) |
| `sibawayh_abniya_raw/` | النص الخام للصفحات 242–303 (4 ملفات) | مرجع استخراج |
| `arabic_verb_tree*.xlsx` | ~11808 فعلاً مصنّفة بمجالات WordNet (verb.body…) مع جذور مرشحة من AWN | ⚠️ **مبنية على WordNet/AWN — لا تُستعمل مصدراً للأنواع الدلالية في النواة (محظور دستوري)**؛ الجذور فيها «مرشحة» |

---

## 4. العلاقة بالمشاريع المجاورة

- **Arabic FrameNet** (`/Users/husseinhiyassat/arabic-net/FrameNet/FrameNet`, انظر `HANDOFF_ARABIC_FRAMENET_USE.md`):
  - يقرأ `awzaan_af3aal_all.csv` **مجمَّداً بالبصمة** `ba0aee78…` و`awzan-sibawayh-308.csv` `a1c1f7f9…`. **أي تعديل على هذين الملفين يكسر مدقّق FrameNet (STOP)** — لا تعدّلهما؛ أي تصحيح = ملف جديد بقرار المالك.
  - FrameNet **لا يغذّي** أنواع النواة الدلالية هنا (محظور دستوري). يجوز استعماله مرجعاً خارجياً للمقارنة فقط، لا مصدراً.
  - مخزون أوزان الأسماء الموسَّع (941 وزناً: سيبويه EXISTS + مؤنث + مشتقات المزيد + نسبة + أوزان المالك) يعيش في `FrameNet/release/layer2_v2/wazn_nouns_inventory.csv`، وليس جزءاً من هذا المستودع.
- **المعاني الجذرية**: `roots-4662-meaning.csv` و`v21-معاني-حسب-الحرف/` في `/Users/husseinhiyassat/hokom-local-validation/taaqol-executor-wt/data/` — تُقرأ بالبصمة عبر وسيط، لا تُنسخ هنا.

---

## 5. قواعد العمل للوكيل

1. لا تعدّل `data/` (بيانات المالك) ولا `wazn_constitution_2.html` ولا `tests/gold/` دون قرار صريح.
2. إصلاح عيب في المحرك = حذف مدخله من `known_defects.py` بعد أن يصير XPASS، مع إعادة تشغيل الشجرة كلها وذكر العدد قبل/بعد.
3. لا تُدخل تطبيعاً أو مطابقة جزئية أو احتمالاً (D-S01/D-S02/D-C01 أمثلة لما يُعدّ عيباً).
4. أي توسيع خارج الجذور العشرة التجريبية (مثل الرباعي أو اللفيف) يبدأ بـ STOP / OWNER_ALERT ما دامت D-M08/D-D09 مفتوحة.
5. التقرير: كتل key=value، بصمات الملفات المتغيّرة، عدد poison/self-check، وما لم يُنجز.

## 6. ما لم يُنجز / مفتوح

- 21 فئة عيب مفتوحة (209 حالة xfail).
- القيم الذهبية والبيانات الثلاث (`awzaan_af3aal_all`, `abniya_sibawayh`, الذهبي) `OWNER_RATIFIED=NO` في ملفاتها.
- README غير متزامن مع الشيفرة.
- تغييرات الاختبارات والبيانات غير مُودَعة في git.
- محرك التوافق احتمالي (يخالف المبدأ ٣) — لم يُستبدل بحكم ثنائي.

## تحديث 2026-11-05 — إغلاق عيوب fail-open و«لا-استنتاج»
أُصلحت خمس فئات (9 حالات) فصار المحرك يرفض بدل أن يمرّ بصمت:
- D-M08: `conjugate`/`derive` ترفعان `NotImplementedError` للّفيف المقرون والمفروق.
- D-D09: `conjugate`/`derive` ترفعان `NotImplementedError` لكل جذر ليس ثلاثة أحرف (الرباعي لا يُقطع).
- D-D10: `_apply_wazn` ترفع `ValueError` لمفتاح وزن غير معروف (لا إسقاط صامت).
- D-S01/D-S02: `_resolve_sem_type`/`_resolve_predicate` مطابقة تامة فقط.
حُذفت الفئات من `tests/known_defects.py`. الحالة: **1929 passed, 200 xfailed** — 16 فئة مفتوحة.
لم تُمسّ القيم الذهبية ولا البيانات. ما زال مفتوحاً: اسم المفعول/الفاعل للازم (كرم → مَكْرُوم، تُثبّته القيم الذهبية — قرار المالك)، وباب فَعِلَ يَفْعِلُ غير معرَّف، و`MITHAL_YAA` يُصرَّف بمُصرِّف الصحيح.

## تحديث 2026-11-05 (٢) — اسم مفعول فَعُلَ (المالك: «نعم، صحّح كرم»)
- `derive`: باب فَعُلَ يَفْعُلُ لازم دائماً، فـ`ism_mafuul = None` (إلا إن خزّن المالك قيمة).
- الذهبي: `كرم|I.mafuul|∅`؛ اصطلاح جديد C6 (`∅` = لا صيغة مرخَّصة، والمحرك يعيد None).
- بقي شكلاً فقط: اسم الفاعل كَارِم (قليل في فَعُلَ لا ممتنع)، ومجهول كَرُمَ في التصريف.
- التعدية لغير فَعُلَ (جلس، ذهب…) تحتاج حقلاً في pilot_roots.json — غير موجود؛ قرار المالك.
