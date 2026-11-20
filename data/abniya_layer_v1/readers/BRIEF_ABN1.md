# BRIEF_ABN1 — reading the remarks in Sibawayh's abniya list (blind reader)

The input is `PACKET.tsv`: 290 rows from Sibawayh's list of the abniya of nouns and adjectives (al-Kitab vol. 4, pp. 242–303). Each row is a pattern with:
- its status in the source: `EXISTS`, `RARE` or `NOT_FOUND_IN_ARABIC`;
- a remark (`remark`);
- the remark of the previous row (`prev_id_remark`).

Your task is to read the remark of **every row** and decide what it says about the **scope** of the status and its **conditions**. Judge from the row's text alone. Do not consult any other file or any other reader's work. Do not use the web.

## The output: one TSV row for each input row (290 rows, in the same order)
Columns: `id	scope	in_fil	conditions	inherit_from	quote	note`

1. **scope** — what the status covers. Choose exactly one:
   - `KALAM_ALL`: the remark denies (or affirms) the pattern in all speech («ليس في الكلام»، «لا نعلم في الكلام»).
   - `ISM_SIFA`: the ruling is limited to nouns and adjectives («ليس في الأسماء والصفات»).
   - `ISM_ONLY`: the ruling is limited to nouns.
   - `SIFA_ONLY`: the ruling is limited to adjectives.
   - `EXCEPT_JAM`: the pattern is denied except as a broken plural («إلا أن يكسر عليه للجمع»، «إلا للجمع»).
   - `JAM_ONLY`: the pattern exists only as a plural.
   - `TANITH_DEPENDENT`: the ruling depends on whether the alif marks the feminine.
   - `NOT_ABOUT_SCOPE`: the remark does not touch scope, e.g. «يمتد إلى ص243» or a note on vocalisation.
   - `OTHER`: none of the above. Explain in `note`.
2. **in_fil**:
   - `YES` if the remark says the pattern occurs in verbs («ويكون في الفعل»).
   - `NO` if it denies that.
   - `UNSTATED` otherwise.
3. **conditions** — zero or more of the following, separated by `;`, in alphabetical order. Write `NONE` if there are none.
   - `PAGE_SPAN`: the entry continues on another page.
   - `RARE_ISM`: rare in nouns.
   - `RARE_SIFA`: rare in adjectives, or the adjective use comes only in a set expression.
   - `FEW_WORDS`: the remark says the pattern has only one word or a few named words («لا نعلمه إلا في…»، «حرف واحد»).
   - `FEM_MARK_REQUIRED`: the pattern requires a feminine marker.
   - `PLURAL_RELATED`: the remark ties the pattern to plurals.
   - `SAME_LIST_AS_PREV`: the remark refers the row to a list or sentence in an earlier row («من القائمة نفسها»، «من الجملة نفسها»).
   - `VOCALIZATION_NOTE`: a note on vocalisation, or a doubt about it.
   - `DIALECT_OR_VARIANT`: a variant reading or dialect.
   - `OTHER`: anything else. Explain in `note`.
4. **inherit_from** — if the row takes its ruling from an earlier row (`SAME_LIST_AS_PREV`), give the id of the first row of that list, the row whose remark has the full sentence. Otherwise write `—`.
   - When `inherit_from` is set, `scope` is the scope of that full sentence as it applies to this pattern, e.g. «إلا للجمع» → `EXCEPT_JAM`.
5. **quote** — Sibawayh's wording between «» exactly as it appears in the remark, or `—` if there is none.
6. **note** — one short line, or `—`.

## Rules
- Read every row. Do not skip a row or sample.
- Do not change the source status, and do not judge whether the pattern exists in Arabic yourself. Your job is only to classify what the remark says.
- When unsure, choose `OTHER` and explain.
- Write UTF-8 TSV with no extra quoting, to the path you are given. Then check it: 291 lines including the header, and the ids in the same order as the input.
