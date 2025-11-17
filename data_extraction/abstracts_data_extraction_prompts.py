USER_ABSTRACT_PAIRS_PROMPT = """
Please extract tumour–stain or neoplasm–stain pairs from the following abstract:

Study title for context: 
{study_title}
Abstract:
{abstract}
""".strip()

SYSTEM_ABSTRACT_PAIRS_PROMPT = """
You will be provided with a scientific abstract of a study. Your task is to identify all pairs of ovarian tumours, tumour histological types, or neoplasms and their associated immunostains mentioned in the text.

For each ovarian tumour type / neoplasm type and corresponding immunohistochemical stain pair mentioned in the provided abstract, please extract the following information (where available):

<OUTPUT_FORMAT>
Provide output as a json, beginning with ```json

Fields:
"tumour": string (tumour name or neoplasm name)
"stain": string (name of immunohistochemical / immuno stain used)
"pattern": string (location / pattern of staining, e. g.: cytoplasmic, membranous, nuclear, stromal, epithelial, etc.)
"expr_type": string (expression type, only one of: loss, over-expression, positive, negative, aberrant, mutant, wild-type, mixed, altered. If multiple apply and can't be distinguished, prefer 'altered' or 'mixed' if appropriate, otherwise prioritize more specific types like 'loss' or 'overexpression' over 'positive'.)
"total_N": int (total number of samples (patients) analyzed for a given pair [N])
"expr_n": int (number of samples (patients) showing specified expression type for that given pair [n])
"expr_pct": float (percentage of samples (patients) with expression type for that given pair [%])
"expr_score": string (expression score, e.g. "1+", "++", "3", "0", "-")
"expr_threshold": string (expression of cells expressing the protein that stain binds to, e.g. "<5%", ">20%", "10-15%") Please use strict formatting only <, >, <=, >= or a range like "10-15%". 
"expr_intensity": string (expression strength described as adjective, e.g. low, weak, moderate, high, very high)
"expr_distribution": string (expression distribution pattern: focal, diffuse, block, unknown)
"group": string (group name if pairs are categorized into different groups like Grade, FIGO stage, age, morphological specifics, etc.)
"group_cat": string (particular category within the group, e.g. Grade 1, FIGO stage I, age 50-60, etc.)
"notes": string (additional observations or comments, 5 words max)

Omit any null/empty fields from output.
</OUTPUT_FORMAT>

<EXPRESSION_RULES>
Make sure that each possible value of score, threshold and intensity is preserved as a separate dict.

Do not omit any scores for a given cancer-stain pair. 

Each score should be treated separately. 1+ should not contain 2+ and so on, unless specified in the abstract otherwise. 

If multiple scores/intensities are given for the same tumour-stain pair without clear distinction (e.g., "weak to moderate"), create separate entries if they refer to distinct sub-populations or scoring criteria, otherwise try to capture the range or primary description.

Score marked as minus "-" or "0" implies negative expression type; mark pairs with such score as with negative expression type if not otherwise specified.

"Over-expression" should never be calculated from the number of positive samples; it must be directly stated in the text.

High expression is not the same as over-expression.

Any expression type other than 'positive' (e.g., loss, over-expression, aberrant, mutant) must be directly stated in the text. If a stain is present, default to "positive" unless a more specific type is given.

**Determining Expression Type (`expr_type`):**

1.  **Prioritize Explicit Labels:** Always use the exact terminology from the source for `expr_type` if it provides specific labels like "positive", "negative, "loss", "over-expression", "aberrant", "altered", "mutant", "wild-type", etc.

2.  **Defining "Negative" Expression:** Set `expr_type` to "negative" ** if:
    * The source explicitly uses terms like "negative".
    * All samples for a given pair receive a score that is explicitly defined as negative (e.g., a score of "0" or "-").

3.  **Defining "Positive" Expression:**
    * In all other cases where staining is assessed for its presence, the default `expr_type` is "positive".
    * **Crucially:** If the source assesses for positivity (e.g., the column in a table is "Positive cases (%)") and finds that 0 out of N samples are positive, you MUST represent this as `{"expr_type": "positive", "expr_n": 0, "expr_pct": 0}`.
    * Do **not** change the `expr_type` to "negative" just because the count of positive samples is zero. This correctly captures that the *test for positivity* was performed and the result was zero.

Reporting `expr_n` and `expr_pct`:
The values for `expr_n` (number of samples) and `expr_pct` (percentage) must always correspond to the `expr_type` you have assigned.
* **Example 1:** If the source states "p53 positive: 80/100 (80%)", the output should have `"expr_type": "positive"`, `"expr_n": 80`, `"expr_pct": 80`.
* **Example 2:** If the source states "p53 positive: 0/100 (0%)", the output must be `"expr_type": "positive"`, `"expr_n": 0`, `"expr_pct": 0`.
* **Example 3:** If the source states "All cases were negative for p53" for 100 cases, the output should be `"expr_type": "negative"`, `"expr_n": 100`, `"expr_pct": 100`.
* **Example 4:** If the source states "50 cases were negative for p53" for 100 cases, the output should be `"expr_type": "negative"`, `"expr_n": 50`, `"expr_pct": 50`.

"Yes" implies positive expression type, while "No" implies negative expression type.

Remember: if the expression type is negative, the expression threshold should fall within the left value range (≤/< expr_threshold)
</EXPRESSION_RULES>

<GENERAL_RULES_TO_FOLLOW>
Please do not interpret provided sensitivity or specificity values as a expression percentage "expr_pct". For instance if authors state that stain XYZ showed sensitivity of 68% for a given tumour type, this is not the same as saying that stain XYZ was expressed in 68% of samples of that tumour type. Ignore sensitivity and specificity values in the text.

When two stains are applied simultaneously or a combination result is given—such as "PAX-8 positive, WT1 negative" or "SATB2 (-) / PAX8 (+)" — ignore such pairs unless the results for each stain can be clearly separated and extracted individually.

Extract explicitly stated names of ovarian cancers from the text, and expand abbreviations where they are clearly defined in the context. Do not group pairs into larger groups that contain more than one type of tumor unless the text does so explicitly.

Please focus on primary ovarian tumors types / ovarian neoplasms; do not count metastases to other tissues or lymph nodes unless the cancer type itself is "metastatic ovarian cancer" or similar.

The intensity (e.g. low, weak, moderate, high, very high) and distribution of the staining (e.g. focal, diffuse, block) is not the same as staining pattern (nuclear, membranous or cytoplasmic).

Do not perform any calculations (e.g., percentages from whole numbers or vice versa). Use only numbers directly stated in the text.

Do not hallucinate any data; if it isn't directly stated in the text, your output shouldn't contain it for that specific field.

Only use the data found within the provided text.

Extract data for all possible ovarian cancer-stain pairs mentioned.

If provided by the text, always include the expression threshold, intensity, and score.

Keep the additional comments 5 words max each. Note if tissue microarrays (TMAs) were used with "TMA" in the comment.

If pairs are categorized into different groups such as Grade, FIGO stage, age, tumour site, or morphological specifics, include the group name in the 'group' field and specify the particular category within that group in the 'group_cat' field.

Researchers sometimes report the mean percentage of stained cells or stained area on a slide (e.g., “mean 20% of cells stained”). - Ignore that, as this is not the same as expr_pct, which refers to the percentage of patient samples that show a given expression type.
</GENERAL_RULES_TO_FOLLOW>


<BAD_ABSTRACT_RULES>
If the abstract doesn't contain the requested data, output only: BAD ABSTRACT.

Make sure that you are sure which stain was applied on what tumour type, if the data is not clear, output also BAD ABSTRACT.

If no tumors names / neoplasm names are present output BAD ABSTRACT.
</BAD_ABSTRACT_RULES>

Remember to encapsulate the JSON output in a list, like `[ { ... }, { ... } ]`.
Start your output with ```json

Here are some examples:

<example>
Study title: 
Differential vimentin expression in ovarian and uterine corpus endometrioid adenocarcinomas: diagnostic utility in distinguishing double primaries from metastatic tumors 
Abstract:
This study aimed to assess the diagnostic value of vimentin expression in differentiating endometrioid adenocarcinoma of primary uterine corpus and ovarian origin. Immunohistochemical analyses for the expression of vimentin in
tumoral epithelial cells were performed on 149 endometrioid adenocarcinomas wherein the primary sites were not in question, including whole tissue sections of 27 carcinomas of uterine corpus origin (and no synchronous ovarian tumor), 7
carcinomas of ovarian origin (and no synchronous uterine corpus tumor) and a tissue microarray (TMA) containing 91 primary uterine corpus and 24 primary ovarian carcinomas. We also assessed 15 cases that synchronously involved the uterine
corpus and ovary, 15 cases of metastasis to organs/tissues other than uterine corpus or ovary as well as 7 lymph node metastases. Vimentin was negative in 97% (30/31) of primary ovarian carcinomas. In contrast, 82% (97/118) of primary
uterine corpus carcinomas were vimentin-positive. Vimentin expression was discordant in 53% of synchronous tumors. The sensitivity and specificity of negative vimentin staining in predicting an ovarian primary were 97% and 82%, respectively, whereas parallel values for positive vimentin staining in predicting a primary uterine tumor were 82% and 97%, respectively. The pattern of vimentin expression in all cases was maintained in their respective regional lymph nodes and distant metastases. In conclusion, ovarian and uterine corpus endometrioid adenocarcinomas have different patterns of vimentin expression. If validated in larger and/or different data sets, these findings may have diagnostic value in distinguishing
metastatic lesions from double primary tumors involving both sites.

Example output:
```json
[
  {
    "tumour": "endometrioid adenocarcinoma of ovarian origin",
    "stain": "vimentin",
    "expr_type": "negative",
    "total_N": 31,
    "expr_n": 30,
    "expr_pct": 97
  }
]
```
</example>

<example>
Study title: 
Dual Immunostain With SATB2 and CK20 Differentiates Appendiceal Mucinous Neoplasms From Ovarian Mucinous Neoplasms.
Abstract:
OBJECTIVES: Determination of the primary site of origin for mucinous neoplasms identified in the peritoneal and/or pelvic cavities may be challenging, with major differential diagnoses including appendiceal mucinous neoplasm (AMN) and ovarian mucinous neoplasm (OMN). Special AT-rich sequence binding protein 2 (SATB2) has been shown to be highly selectively expressed in the lower gastrointestinal tract, including the appendix. METHODS: We investigated the utility of a dual stain (DS) with SATB2 or caudal type homeobox 2 (CDX2) and cytokeratin 20 (CK20) or villin in distinguishing AMNs from OMNs. Tissue microarrays with 40 AMNs and 18 OMNs were stained with SATB2 or CDX2 paired with either CK20 or villin. RESULTS: SATB2 single stain showed a good sensitivity of 83% and the highest specificity of 78% for AMNs over OMNs among all four stains. DS with SATB2 and villin showed an identical sensitivity of 78% but specificity increased to 94%, while DS with SATB2 and CK20 showed a sensitivity of 80% and a specificity of 100%. In contrast, DS with CDX2 and CK20/villin showed slightly higher sensitivity but much lower specificity. CONCLUSIONS: DS with SATB2/CK20 shows the greatest potential clinical utility in distinguishing AMNs from OMNs and is superior to DS with CDX2/CK20. Importantly, DS could be helpful for specimens with limited tissues.
Example output:
```json
[
  {
    "stain": "villin",
    "notes": "TMA",
    "total_N": 18,
    "tumour": "Ovarian mucinous neoplasm"
  },
  {
    "stain": "CDX2",
    "notes": "TMA",
    "total_N": 18,
    "tumour": "Ovarian mucinous neoplasm"
  },
  {
    "stain": "SATB2",
    "notes": "TMA",
    "total_N": 18,
    "tumour": "Ovarian mucinous neoplasm"
  },
  {
    "stain": "CK20",
    "notes": "TMA",
    "total_N": 18,
    "tumour": "Ovarian mucinous neoplasm"
  },
  {
    "stain": "villin",
    "notes": "TMA",
    "total_N": 40,
    "tumour": "appendiceal mucinous neoplasm"
  },
  {
    "stain": "CDX2",
    "notes": "TMA",
    "total_N": 40,
    "tumour": "appendiceal mucinous neoplasm"
  },
  {
    "stain": "SATB2",
    "notes": "TMA",
    "total_N": 40,
    "tumour": "appendiceal mucinous neoplasm"
  },
  {
    "stain": "CK20",
    "notes": "TMA",
    "total_N": 40,
    "tumour": "appendiceal mucinous neoplasm"
  }
]
```

</example>

<example>
Study title: 
Comparative analysis of Napsin A, alpha-methylacyl-coenzyme A racemase (AMACR, P504S), and hepatocyte nuclear factor 1 beta as diagnostic markers of ovarian clear cell carcinoma: an immunohistochemical study of 279 ovarian tumours.
Abstract:
Napsin A and α-methylacyl-coenzyme A racemase (AMACR, P504S) have recently been described as being frequently expressed in clear cell carcinomas (CCC) of the gynecological tract. The present study was conducted to assess the test performance of these newer markers relative to the more traditional marker, hepatocyte nuclear factor 1β (HNF1β), in a large and histotypically diverse dataset. A total of 279 ovarian tumours in tissue microarrays were immunohistochemically assessed for the expression of Napsin A, AMACR and HNF1β. HNF1β showed nuclear staining. HNF1β, Napsin A and AMACR were expressed in 92%, 82% and 63% of 65 CCC, 7%, 1% and 1% of 101 serous carcinomas, 37%, 5.3% and 0% of 19 endometrioid carcinomas, 60%, 0% and 0% of 45 mucinous tumours, 100%, 0% and 0% of seven yolk sac tumours, and 0%, 16.7% and 16.7% of six steroid cell tumours NOS, respectively. All other tumours, including 18 adult-type granulosa cell tumours, eight dysgerminomas and nine other miscellaneous tumour types were negative for all three markers. Using a benchmark of ≥1% of tumour cells for positivity and CCC as the diagnostic end-point, the sensitivity, specificity, negative predictive value and positive predictive value of Napsin A expression were 0.82, 0.99, 0.94, and 0.98, respectively (odds ratio 439, p < 0.0001). Respective parameters were 0.92, 0.79, 0.97, and 0.58 (odds ratio 44, p < 0.0001) for HNF1β and 0.63, 0.99, 0.89, and 0.5 (odds ratio 112, p < 0.0001) for AMACR. The combination of any two positive markers, irrespective of the staining pattern of the third, significantly predicted the CCC histotype in every analytic scenario. In summary, HNF1β is highly sensitive but is suboptimally specific in isolation, whereas AMACR is highly specific but is suboptimally sensitive. Napsin A is specific but of intermediate sensitivity. Napsin A, AMACR and HNF1β are all viable markers of CCC that can be deployed as components of larger panels when CCC is a diagnostic consideration.

Example output:
```json
[
    {
        "expr_pct": 92.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "HNF1beta",
        "total_N": 65,
        "tumour": "clear cell carcinoma"
    },
    {
        "expr_pct": 82.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "Napsin A",
        "total_N": 65,
        "tumour": "clear cell carcinoma"
    },
    {
        "expr_pct": 63.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "AMACR",
        "total_N": 65,
        "tumour": "clear cell carcinoma"
    },
    {
        "expr_pct": 7.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "HNF1beta",
        "total_N": 101,
        "tumour": "serous carcinoma"
    },
    {
        "expr_pct": 1.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "Napsin A",
        "total_N": 101,
        "tumour": "serous carcinoma"
    },
    {
        "expr_pct": 1.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "AMACR",
        "total_N": 101,
        "tumour": "serous carcinoma"
    },
    {
        "expr_pct": 37.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "HNF1beta",
        "total_N": 19,
        "tumour": "endometrioid carcinoma"
    },
    {
        "expr_pct": 5.3,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "Napsin A",
        "total_N": 19,
        "tumour": "endometrioid carcinoma"
    },
    {
        "expr_pct": 0.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "AMACR",
        "total_N": 19,
        "tumour": "endometrioid carcinoma"
    },
    {
        "expr_pct": 60.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "HNF1beta",
        "total_N": 45,
        "tumour": "mucinous tumour"
    },
    {
        "expr_pct": 0.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "Napsin A",
        "total_N": 45,
        "tumour": "mucinous tumour"
    },
    {
        "expr_pct": 0.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "AMACR",
        "total_N": 45,
        "tumour": "mucinous tumour"
    },
    {
        "expr_pct": 100.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "HNF1beta",
        "total_N": 7,
        "tumour": "yolk sac tumour"
    },
    {
        "expr_pct": 0.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "Napsin A",
        "total_N": 7,
        "tumour": "yolk sac tumour"
    },
    {
        "expr_pct": 0.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "AMACR",
        "total_N": 7,
        "tumour": "yolk sac tumour"
    },
    {
        "expr_pct": 0.0,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "HNF1beta",
        "total_N": 6,
        "tumour": "steroid cell tumour NOS"
    },
    {
        "expr_pct": 16.7,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "Napsin A",
        "total_N": 6,
        "tumour": "steroid cell tumour NOS"
    },
    {
        "expr_pct": 16.7,
        "expr_threshold": ">=1%",
        "expr_type": "positive",
        "notes": "TMA",
        "stain": "AMACR",
        "total_N": 6,
        "tumour": "steroid cell tumour NOS"
    },
    {
        "expr_n": 18,
        "expr_pct": 100.0,
        "expr_threshold": "<1%",
        "expr_type": "negative",
        "notes": "TMA",
        "stain": "HNF1beta",
        "total_N": 18,
        "tumour": "adult-type granulosa cell tumour"
    },
    {
        "expr_n": 18,
        "expr_pct": 100.0,
        "expr_threshold": "<1%",
        "expr_type": "negative",
        "notes": "TMA",
        "stain": "Napsin A",
        "total_N": 18,
        "tumour": "adult-type granulosa cell tumour"
    },
    {
        "expr_n": 18,
        "expr_pct": 100.0,
        "expr_threshold": "<1%",
        "expr_type": "negative",
        "notes": "TMA",
        "stain": "AMACR",
        "total_N": 18,
        "tumour": "adult-type granulosa cell tumour"
    },
    {
        "expr_n": 8,
        "expr_pct": 100.0,
        "expr_threshold": "<1%",
        "expr_type": "negative",
        "notes": "TMA",
        "stain": "HNF1beta",
        "total_N": 8,
        "tumour": "dysgerminoma"
    },
    {
        "expr_n": 8,
        "expr_pct": 100.0,
        "expr_threshold": "<1%",
        "expr_type": "negative",
        "notes": "TMA",
        "stain": "Napsin A",
        "total_N": 8,
        "tumour": "dysgerminoma"
    },
    {
        "expr_n": 8,
        "expr_pct": 100.0,
        "expr_threshold": "<1%",
        "expr_type": "negative",
        "notes": "TMA",
        "stain": "AMACR",
        "total_N": 8,
        "tumour": "dysgerminoma"
    },
    {
        "expr_n": 9,
        "expr_pct": 100.0,
        "expr_threshold": "<1%",
        "expr_type": "negative",
        "notes": "TMA",
        "stain": "HNF1beta",
        "total_N": 9,
        "tumour": "other miscellaneous tumour type"
    },
    {
        "expr_n": 9,
        "expr_pct": 100.0,
        "expr_threshold": "<1%",
        "expr_type": "negative",
        "notes": "TMA",
        "stain": "Napsin A",
        "total_N": 9,
        "tumour": "other miscellaneous tumour type"
    },
    {
        "expr_n": 9,
        "expr_pct": 100.0,
        "expr_threshold": "<1%",
        "expr_type": "negative",
        "notes": "TMA",
        "stain": "AMACR",
        "total_N": 9,
        "tumour": "other miscellaneous tumour type"
    }
]
```
</example>

<example>
Study title:
The fading guardian: clinical relevance of TP53 null mutation in high-grade serous ovarian cancers 

Abstract:
BACKGROUND: we evaluated the concordance between immunohistochemical p53 staining and TP53 mutations in a series of HGSOC. Moreover, we searched for prognostic differences between p53 overexpression and null
expression groups. METHODS: patients affected by HGSOC were included. For each case p53 immunohistochemical staining and molecular assay (Sanger sequencing) were performed. Kaplan-Meier survival analyses were undertaken to
determine whether the type of TP53 mutation, or p53 staining pattern influenced overall survival (OS) and progression free survival (PFS). RESULTS: 34 HGSOC were considered. All cases with a null immunohistochemical p53 expression (n=16)
showed TP53 mutations (n=9 nonsense, n=4 in-frame deletion, n=2 splice, n=1 in-frame insertion). 16 out of 18 cases with p53 overexpression showed TP53 missense mutation. Follow up data were available for 33 out of 34 cases (median follow
up time 15 month). We observed a significant reduction of OS in p53 null group [HR = 3.64, 95% CI 1.01-13.16]. CONCLUSION: immunohistochemical assay is a reliable surrogate for TP53 mutations in most cases. Despite the small cohort and
the limited median follow up, we can infer that HGSOC harboring p53 null mutations are a more aggressive subgroup.

Example output:
```json
[
  {
    "tumour": "high-grade serous ovarian cancer",
    "stain": "p53",
    "expr_type": "loss",
    "total_N": 34,
    "expr_n": 16,
    "notes": "Loss cases had TP53 mutations"
  },
  {
    "tumour": "high-grade serous ovarian cancer",
    "stain": "p53",
    "expr_type": "overexpression",
    "total_N": 34,
    "expr_n": 18
  }
]
```
</example>
""".strip()

