CLASSIFICATION_PROMPT = """
You are an expert in oncology and pathology, with deep knowledge of the WHO Classification of Female Genital Tumours (5th Edition, 2020)—commonly referred to as the WHO Blue Book—specifically focusing on ovarian tumours.

Your task is to map each tumour name from the study below to the most precise and relevant category from the WHO Blue Book classification provided. For each mapping, you must also provide a brief justification for your choice.

**WHO 2020 Categories for Ovarian Tumours**
{categories}

**Supplemental Categories**
If a tumour name does not correspond to any official WHO ovarian tumour category, use one of the two supplemental categories defined below:
- **Not Ovarian**: Tumour type clearly originates outside the ovary or does not belong to primary ovarian tumour pathology. (e.g., "Metastatic breast cancer", "Cervical carcinoma").
- **Artificial Taxon**: Term is a non-standard, informal, outdated, or overly broad grouping not recognized as a specific diagnostic entity by the WHO. This is often used for study-defined subgroups or composite clinical terms. (e.g., "Epithelial ovarian cancer," "non-serous carcinoma," "ovarian carcinoma").

**Guiding Principles**

1.  **Precision First:** Always aim for the most specific, terminal category in the WHO list (e.g., map "High-grade serous carcinoma" to "High-grade serous carcinoma", not the broader "Malignant Serous Tumours") (As low category as possible).
2.  **Generalize When Necessary:** If a tumour name is valid but not specific (e.g., "Serous carcinoma"), and the study context does not provide enough detail to specify a subtype (like high-grade vs. low-grade), map it to the most appropriate intermediate or general category (e.g., "Malignant Serous Tumours").
3.  **Modernize Outdated Terms:** If a study uses an outdated term (e.g., "Serous cystadenocarcinoma"), map it to its modern equivalent in the 2020 WHO classification (e.g., "Malignant Serous Tumours" or a more specific subtype if context allows).
4.  **Use Supplemental Categories as a Last Resort:** Only use "Artificial Taxon" or "Not Ovarian" if the term cannot be logically mapped to any official WHO category.
5.  **Safety Net:** When in doubt, or if a term is completely unmappable or ambiguous, use "Artificial Taxon". Do not guess.

**Instructions:**

1.  **Analyze Study Context:** Carefully review the study's title, abstract, and publication year to understand its focus and interpret potentially ambiguous or outdated terminology.
2.  **Map Each Tumour:** For each tumour name in the list, follow the Guiding Principles to find the single best corresponding category from the provided WHO classification or a supplemental category.
3.  **Justify Each Mapping:** For every tumour name, provide a concise one-sentence justification explaining why you selected that specific WHO category or supplemental category.
4.  **Format the Output:** Present the results in a clear JSON array. Each object in the array must contain the index, the original tumour name, and the final mapping.

**Output Format:**
Present the results in a JSON array. DO NOT include any text or explanations outside of the JSON structure itself.
```json
[
    {{
        "idx": 1,
        "justification": "Insert one sentence justification here.",
        "tumour": "ovarian mucinous adenocarcinoma",
        "who_mapping": "Mucinous carcinoma of the ovary"
    }},
    {{
        "idx": 2,
        "justification": "Insert one sentence justification here.",
        "tumour": "ovarian serous carcinoma",
        "who_mapping": "Malignant Serous Tumours"
    }},
    {{
        "idx": 3,
        "justification": "Insert one sentence justification here.",
        "tumour": "ovarian carcinoma",
        "who_mapping": "Artificial Taxon"
    }}
]
````

**Study Information for context:**

  * **Title:** {title}
  * **Abstract:** {abstract}
  * **Study Publication Year:** {publication_year}

**Tumour Entries to Map:**
Each tumour is represented as a dictionary with at least the `"tumour"` key. Optional metadata includes:

  - `"group"`: A higher-level grouping or context for the tumour type.
  - `"group_category"`: A sub-classification or refinement under the group.
  - `"notes"`: Additional extracted context that may help with disambiguation.

Here is the list of tumour names to classify:

```json
{tumour_names}
```

""".strip()



CLASSIFICATION_PROMPT_NO_JUSTIFICATION = """
You are an expert in oncology and pathology, with deep knowledge of the WHO Classification of Female Genital Tumours (5th Edition, 2020)—commonly referred to as the WHO Blue Book—specifically focusing on ovarian tumours.

Your task is to map each tumour name from the study below to the most precise and relevant category from the WHO Blue Book classification provided. For each mapping, you must also provide a brief justification for your choice.

**WHO 2020 Categories for Ovarian Tumours**
{categories}

**Supplemental Categories**
If a tumour name does not correspond to any official WHO ovarian tumour category, use one of the two supplemental categories defined below:
- **Not Ovarian**: Tumour type clearly originates outside the ovary or does not belong to primary ovarian tumour pathology. (e.g., "Metastatic breast cancer", "Cervical carcinoma").
- **Artificial Taxon**: Term is a non-standard, informal, outdated, or overly broad grouping not recognized as a specific diagnostic entity by the WHO. This is often used for study-defined subgroups or composite clinical terms. (e.g., "Epithelial ovarian cancer," "non-serous carcinoma," "ovarian carcinoma").

**Guiding Principles**

1.  **Precision First:** Always aim for the most specific, terminal category in the WHO list (e.g., map "High-grade serous carcinoma" to "High-grade serous carcinoma", not the broader "Malignant Serous Tumours") (As low category as possible).
2.  **Generalize When Necessary:** If a tumour name is valid but not specific (e.g., "Serous carcinoma"), and the study context does not provide enough detail to specify a subtype (like high-grade vs. low-grade), map it to the most appropriate intermediate or general category (e.g., "Malignant Serous Tumours").
3.  **Modernize Outdated Terms:** If a study uses an outdated term (e.g., "Serous cystadenocarcinoma"), map it to its modern equivalent in the 2020 WHO classification (e.g., "Malignant Serous Tumours" or a more specific subtype if context allows).
4.  **Use Supplemental Categories as a Last Resort:** Only use "Artificial Taxon" or "Not Ovarian" if the term cannot be logically mapped to any official WHO category.
5.  **Safety Net:** When in doubt, or if a term is completely unmappable or ambiguous, use "Artificial Taxon". Do not guess.

**Instructions:**

1.  **Analyze Study Context:** Carefully review the study's title, abstract, and publication year to understand its focus and interpret potentially ambiguous or outdated terminology.
2.  **Map Each Tumour:** For each tumour name in the list, follow the Guiding Principles to find the single best corresponding category from the provided WHO classification or a supplemental category.
3.  **Format the Output:** Present the results in a clear JSON array. Each object in the array must contain the index, the original tumour name, and the final mapping.

**Output Format:**
Present the results in a JSON array. DO NOT include any text or explanations outside of the JSON structure itself.
```json
[
    {{
        "idx": 1,
        "tumour": "ovarian mucinous adenocarcinoma",
        "who_mapping": "Mucinous carcinoma of the ovary"
    }},
    {{
        "idx": 2,
        "tumour": "ovarian serous carcinoma",
        "who_mapping": "Malignant Serous Tumours"
    }},
    {{
        "idx": 3,
        "tumour": "ovarian carcinoma",
        "who_mapping": "Artificial Taxon"
    }}
]
````

**Study Information for context`:**

  * **Title:** {title}
  * **Abstract:** {abstract}
  * **Study Publication Year:** {publication_year}

**Tumour Entries to Map:**
Each tumour is represented as a dictionary with at least the `"tumour"` key. Optional metadata includes:

  - `"group"`: A higher-level grouping or context for the tumour type.
  - `"group_category"`: A sub-classification or refinement under the group.
  - `"notes"`: Additional extracted context that may help with disambiguation.

Here is the list of tumour names to classify:

```json
{tumour_names}
```

""".strip()
