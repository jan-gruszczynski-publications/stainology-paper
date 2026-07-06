"""
Harmonized IHC stain nomenclature dictionary (ovarian cancer).

Matching model (unchanged from your setup):
    incoming string -> clean (lowercase, strip spaces/hyphens/etc.) -> EXACT match against values.

Greek handling:
    Cleaning does NOT convert Greek letters to text, so each stain that has a Greek
    form lists BOTH the raw Greek-character form (e.g. 'erα', where α = U+03B1 survives
    cleaning) AND the spelled form (e.g. 'eralpha', matched when input was 'ER-alpha').
    No separate Greek normalization map is used.

Isoform policy:
    Distinct isoforms / ligands / receptor subunits are SEPARATE keys
    (ERα vs ERβ; PR-A vs PR-B; VEGF-A/C/D; CD44 splice variants).

Redundancy policy:
    Both cleaned and human-readable (hyphen/space/paren) variants are kept on purpose
    as a double safety measure.
"""

STAINS_VARIATIONS_DICTIONARY = {

    # ---- Actin / smooth muscle ----------------------------------------------
    'alphasmoothmuscle': [
        'alphasmoothmuscleactin',
        'alphasmoothmuscleactin(sma)',
        'alpha-smooth muscle actin',
        'smoothmuscleactin',
        'smooth muscle actin',
        'alphasmoothmuscle',
        'sma',
        'α-sma',
        'alpha-sma',
        'alphasma',
        'asma',
        'msa',  # "muscle specific actin" often α-SMA
    ],

    # ---- Cytokeratin AE1/AE3 -------------------------------------------------
    'ae1ae3': [
        'ae1/ae3',
        'ae1ae3',
        'ae13',
        'ae1/3',
        'ae1/ae3 (cytokeratin)',
        'cytokeratin ae1/ae3',
        'cytokeratin (ae1/ae3)',
        'cytokeratin (ae1/ae3) (antibody)',
        'cytokeratin ae1/ae3 (antibody)',
        'ckae13',
        'ckae1/3',
        'cytokeratinae13',
        'cytokeratinae1ae3',
        'ae1ae3cytokeratins',
        'cytokeratin ae1/3',
        'keratin ae1/ae3',
        'keratinae1ae3',
        'ae1/ae3 cytokeratins',
        'cytokeratin ae1/3',
    ],

    'p53': ['tp53', 'p53', 'p53protein', 'protein53'],
    'her2': ['her2neu', 'cerbb2', 'erbb2', 'her2', 'her-2', 'her2/neu', 'her-2/neu',
             'c-erbb-2', 'c-erbb2', 'her-2neu', 'her2neu'],
    'p16': ['p16ink4a', 'cdkn2a', 'p16', 'p16(ink4a)', 'p16mts1'],
    'arid1a': ['baf250a', 'arid1a', 'baf 250a'],
    'smarca4': ['brg1', 'smarca4', 'smarca4(brg1)', 'smarca4/brg1'],
    'braf': ['ve1', 'braf', 'braf v600e', 'brafv600e', 'braf (ve1)'],
    'met': ['cmet', 'met', 'c-met'],
    'cd117': ['ckit', 'cd117', 'c-kit', 'kit', 'kitprotein', 'kit protein',
              'stemcellfactorreceptor', 'stem cell factor receptor',
              'c-kit (cd117)', 'ckitcd117'],

    # ---- Hormone receptors (SPLIT by isoform) --------------------------------
    'er': [
        'estrogenreceptor', 'oestrogenreceptor', 'esr1', 'er',
        'estrogen receptor', 'oestrogen receptor', 'estrogen-receptor',
        'estrogenreceptorprotein', 'estrogenreceptors', 'oestrogenreceptors',
        'estrogen',
    ],
    'eralpha': [
        'eralpha', 'er-alpha', 'er alpha',
        'erα', 'er-α', 'er α',
        'estrogenreceptoralpha', 'estrogen receptor-alpha', 'estrogen receptor alpha',
        'estrogenreceptorα', 'oestrogenreceptoralpha', 'oestrogen receptor-alpha',
        'estrogenreceptor-alpha', 'estrogen receptor-alpha (eralpha)',
    ],
    'erbeta': [
        'erbeta', 'er-beta', 'er beta',
        'erβ', 'er-β', 'er β',
        'estrogenreceptorbeta', 'estrogen receptor beta', 'estrogenreceptorβ',
        'estrogen receptor beta (erbeta)',
    ],
    # Optional finer ERβ isoforms (uncomment if you want them tracked separately):
    # 'erbeta1': ['erbeta1', 'erβ1'],
    # 'erbeta2': ['erbeta2', 'erβ2'],
    # 'erbeta5': ['erbeta5', 'erβ5'],

    'pr': [
        'progesteronereceptor', 'pgr', 'pr', 'nr3c3',
        'progesterone receptor', 'progesterone',
        'progesteronereceptors', 'progesteronereceptorprotein',
    ],
    'pra': [
        'pra', 'pr-a', 'progesteronereceptora',
        'progesteronereceptorsubtypea', 'progesterone receptor subtype a',
    ],
    'prb': [
        'prb', 'pr-b', 'progesteronereceptorb',
        'progesteronereceptorsubtypeb', 'progesterone receptor subtype b',
    ],
    'androgenreceptor': ['ar', 'androgenreceptor', 'androgen receptor', 'androgenreceptors'],

    # ---- Cytokeratins --------------------------------------------------------
    'ck7': ['ck7', 'ck-7', 'ck 7', 'cytokeratin7', 'cytokeratin 7', 'cytokeratin (ck)7', 'keratin7', 'keratin 7'],

    'ck20': ['cytokeratin20', 'cytokeratin 20', 'ck20', 'ck-20', 'ck 20', 'cytokeratin-20'],
    'ck56': ['cytokeratin56', 'ck56', 'ck5/6', 'ck 5/6', 'cytokeratin 5/6', 'keratin 5/6', 'k5/6'],
    'ck18': ['ck18', 'ck 18', 'cytokeratin18', 'cytokeratin 18'],
    'ck19': ['ck19', 'krt19', 'cytokeratin19', 'cytokeratin 19'],
    'cytokeratin': ['ck', 'cytokeratin', 'cytokeratins', 'pan-ck', 'panck', 'pancytokeratin',
                    'pan cytokeratin', 'pankeratin', 'keratin', 'keratins'],

    # ---- Proliferation -------------------------------------------------------
    'ki67': [
        'ki67', 'ki-67', 'ki 67', 'mki67',
        'mib1', 'mib-1', 'mib 1', 'mib1ki67',
        'mib-1 (ki-67)', 'mib-1(ki-67)', 'mib-1 (ki-67 antigen)',
        'ki-67/mib-1', 'ki67 (mib1)', 'ki-67 antigen', 'ki-67-antigen',
        'ki67antigen', 'ki67protein', 'm1b1',
    ],
    'cyclind1': ['cyclind1', 'cyclin d1', 'cyclin-d1', 'ccnd1'],

    # ---- Mismatch repair -----------------------------------------------------
    'mlh1': ['hmlh1', 'mlh1', 'mlh-1', 'mlh1protein'],
    'msh2': ['hmsh2', 'msh2', 'msh-2'],
    'msh6': ['msh6', 'hmsh6'],
    'pms2': ['pms2'],

    # ---- Transcription factors / nuclear -------------------------------------
    'hnf1b': ['hnf1beta', 'hnf1b', 'hnf-1β', 'hnf1β', 'hnf-1beta', 'hnf-1 beta',
              'hnf-1-beta', 'hnf1ss', 'vhnf1', 'hnf1-β', 'hnf1-beta',
              'hepatocyte nuclear factor-1β', 'hepatocyte nuclear factor-1beta'],
    'oct4': ['oct4', 'oct34', 'oct3/4', 'oct-4', 'oct 3/4', 'octamer4', 'octamer-4',
             'pou5f1', 'oct-4 (pou5f1)'],
    'folr1': ['fralpha', 'folr1', 'frα', 'folatereceptoralpha', 'folate receptor alpha',
              'alpha-folate receptor', 'folralpha', 'alpha-fr'],

    # ---- Adhesion / cytoskeleton ---------------------------------------------
    'vimentin': ['vim', 'vimentin'],
    'ema': ['epithelialmembraneantigen', 'ema', 'epithelial membrane antigen',
            'epithelial membrane antigen (ema)', 'ema/muc1'],
    'ecadherin': [
        'ecadherin', 'e-cadherin', 'ecad', 'e-cad', 'ecadh', 'e-cadh',
        'ecd', 'e-cd', 'cdh1',
    ],
    'ncadherin': ['ncadherin', 'n-cadherin', 'n cadherin', 'n-cd', 'n cd'],

    'gammacatenin': ['γcatenin', 'gammacatenin', 'γ-catenin', 'gamma-catenin'],
    'betacatenin': ['βcatenin', 'betacatenin', 'β-catenin', 'beta-catenin', 'ctnnb1'],
    'alphacatenin': ['αcatenin', 'alphacatenin', 'α-catenin', 'alpha-catenin'],
    'deltacatenin': ['δcatenin', 'deltacatenin', 'δ-catenin', 'delta-catenin'],

    'claudin18': ['claudin18.2', 'cldn18', 'claudin18', 'claudin-18', 'claudin 18',
                  'cldn18.2', 'claudin 18.2', 'claudin18.2'],

    # ---- CD44 (SPLIT: standard vs splice variants) ---------------------------
    'cd44': ['cd44', 'cd44s', 'cd44std', 'standardcd44', 'cd44h', 'cd44 antigen',
             'scd44std'],
    'cd44v3': ['cd44v3', 'cd44-v3', 'cd44 v3', 'cd44-v3 isoform', 'scd44v3'],
    'cd44v5': ['cd44v5', 'cd44-v5', 'cd44 v5', 'scd44v5'],
    'cd44v6': ['cd44v6', 'cd44-v6', 'cd44 v6', 'cd44 variant 6', 'cd44-v6 isoform', 'scd44v6'],
    'cd44v7': ['cd44v7', 'cd44 v7', 'cd44v7/8'],
    'cd44v9': ['cd44v9', 'cd44-v9'],
    'cd44v10': ['cd44v10', 'cd44-v10'],
    'cd44v8_10': ['cd44v8-10'],

    'd240': ['podoplanin', 'd240', 'd2-40', 'pdpn'],

    # ---- Inhibin (FIX: no bare 'alphasubunit'/'betaasubunit') ----------------
    'inhibin': [
        'inhibin', 'inhibinalpha', 'alphainhibin', 'inhibinantibody',
        'inhibin alpha', 'alpha-inhibin', 'inhibin alpha subunit',
        'inhibinalphasubunit', 'inhibin alpha-subunit', 'inhibinalpha-subunit',
        'inhibinα', 'inhibin α', 'α-inhibin', 'inhibinαsubunit',
        'inhibin α subunit', 'inhibin-alpha', 'anti-inhibin', 'inibin',
    ],

    # ---- VEGF family (SPLIT: ligands are separate) ---------------------------
    'vegf': ['vegf', 'vascularendothelialgrowthfactor', 'vascular endothelial growth factor',
             'vascular endothelial growth factor (vegf)', 'vegf protein', 'vegf mrna'],
    'vegfa': ['vegfa', 'vegf-a', 'vegf a'],
    'vegfc': ['vegfc', 'vegf-c'],
    'vegfd': ['vegfd', 'vegf-d'],
    'vegfr1': ['vegfr1', 'vegfr-1', 'vegf-r1', 'flt-1', 'flt1', 'flt'],
    'vegfr2': ['vegfr2', 'vegfr-2', 'vegf-r2', 'kdr', 'flk-1', 'kdr/flk-1',
               'vegf receptor 2', 'vegf receptor-2'],
    'vegfr3': ['vegfr3', 'vegfr-3', 'vegf-r3', 'flt-4'],

    # ---- Hypoxia (Greek) -----------------------------------------------------
    'hif1alpha': ['hif-1α', 'hif1α', 'hif-1alpha', 'hif1-α', 'hif1-alpha',
                  'hif-1 alpha', 'hypoxia-inducible factor 1alpha',
                  'hypoxia-inducible factor-1alpha (hif-1alpha)'],
    'hif2alpha': ['hif-2α', 'hif2α', 'hif-2alpha'],

    # ---- NF-kB (Greek kappa) -------------------------------------------------
    'nfkb': ['nf-κb', 'nfκb', 'nfkb', 'nf-kappab', 'nf-κb p65', 'nf-κbp65',
             'nfkbp65', 'nf-kappab p65', 'nf-kappabp65', 'nf-kappab1', 'nfkb1',
             'nf-κb1', 'nf-κb (p65)'],

    # ---- Other markers -------------------------------------------------------
    'p27': ['p27', 'p27kip1', 'p27(kip1)'],
    'glypican3': ['glypican3', 'gpc3', 'glypican-3', 'glypican 3', 'gpc-3', 'glyp-3'],
    'amacr': ['amacr', 'amacrp504s', 'amacr (p504s)', 'p504s'],
    'lewisy': ['lewisy', 'lewisyantigen', 'lewis y', 'lewis y antigen', 'lewis(y)',
               'lewis(y) antigen', 'lewis-y', 'lewis-y antigen'],
    'mammaglobinb': ['mammaglobinb', 'mammaglobin b', 'mgb-2', 'mgb2'],
    'mammaglobina': ['mammaglobina', 'mammaglobin a', 'mgb1', 'mgb-1'],
    'sstr': ['sstr', 'sst1', 'sst2a', 'sst3', 'sst4', 'sst5'],
    'napsin': ['napsin', 'napsina', 'napsin-a', 'napsin a', 'napsa', 'ta02/napsin a'],
    'betahcg': ['hcgbeta', 'antiβhcg', 'betahcg', 'hcg beta', 'β-hcg', 'anti-β-hcg', 'hcgβ'],

    'brca2': ['brca2', 'brca2protein', 'brca2 protein'],
    'wt1': ['wt1', 'wt-1', 'wt1protein', 'wt1 protein', 'wt1 antigen', 'wt-1 antigen',
            'wilms tumor 1', "wilms' tumor 1", 'wilms tumour protein 1 (wt1)',
            "wilms' tumour protein 1 (wt1)", 'wilms tumor gene protein'],
    'pax8': ['pax8', 'pax-8', 'pax 8', 'pax8 pab', 'pax8 mab', 'pax8 (pab)', 'pax8 (mab)',
             'paired box gene 8', 'paired-box gene 8'],
}

STAINS_VARIATIONS_DICTIONARY_FOR_REGEX = {
    'brca1': [
        'brca1',
        'brca1protein',
        r'brca1 \(protein\)',
        'brca1 protein',
    ],
}

EXPR_TYPE_VARIATIONS_DICT = {
    # --- generic detection / intensity ---
    "positive": ["positive"],
    "negative": ["negative", "negative expression", "undetectable"],
    "high": ["high", "high expression", "higher", "highly expressed",
             "high-level expression", "high-expressed", "high density"],
    "low": ["low", "low expression", "lower", "lower expression",
            "low-level expression", "low-expressed", "low density"],
    "intermediate": ["intermediate", "borderline"],
    "equivocal": ["equivocal", "equivocal expression"],
    "mixed": ["mixed", "heterogeneous", "heterogeneity",
              "heterogeneously expressed"],

    # --- relative change / regulation ---
    "increased": ["increased", "increased expression", "elevated",
                  "greater", "enriched"],
    "decreased": ["decreased", "decreased expression", "decrease",
                  "reduced", "reduced expression",
                  "underexpression", "under-expression"],
    "upregulated": ["upregulated", "upregulation", "up-regulated"],
    "downregulated": ["downregulated", "downregulation",
                      "down-regulated", "down-regulation"],

    # --- p53 pattern (dominant in HGSOC) ---
    "overexpression": ["over-expression", "overexpression", "excessive",
                       "overactivation"],
    "loss": ["loss"],  # , "null-type", "deletion"
    # "wild_type":       ["wild-type", "normal"],
    "aberrant": ["aberrant", "abnormal", "altered", "alterations"],
    "mutant": ["mutant", "mutated", "mutation-type"],

    # --- mismatch-repair (MMR) pattern ---
    # "mmr_retained":    ["intact", "retained", "retained expression",
    #                     "preserved", "proficient", "restored expression"],
    # "mmr_deficient":   ["deficient", "deficiency", "dmmr"],

    # --- copy number (HER2 / FISH) ---
    "amplification": ["amplification", "amplified", "polysomy"],
    "no_amplification": ["no amplification"],

    # --- other ---
    "activated": ["activated"],
    "hypermethylation": ["hypermethylation"],
    "polymorphism": ["polymorphism"],
    "not_applicable": ["not applicable"],
}

# OLD
# EXPR_TYPE_VARIATIONS_DICT = {"over-expression": ["over-expression", 'overexpression'],
#                              "increased": ["increased", "elevated"],
#                              "normal": ["normal", "intact"],
#                              "high": ["highexpression", "high", "highexpressed"],
#                              "low": ["low", "low expression", "lowexpression", "low-expression"],
#                              "decreased": ["decreased", "reduced", "underexpression",
#                                            "reduced-expression", "reduced expression", "reduced expression"],
#                              'negative': ['negative', 'negative expression']
#                              }


PATTERN_VARIATIONS_DICT = {
    "nuclear": ['nuclear', 'nucleus', 'tumour cells, nuclear', 'nuclear positive, membranous positive'],
    "membranous": ['membranous', 'membrane',
                   'apical', 'luminal', 'basolateral',
                   'apical membranous', 'basolateral membranous',
                   'apical membrane', 'luminal cell membrane'],
    "cytoplasmic": ['cytoplasmic', 'cytoplasm', 'tumour cells, cytoplasmic',
                    'perinuclear', 'perinuclear or cytoplasmic',
                    'perinuclear cytoplasmic'],
    "stromal": ['stromal', 'stroma', 'stromal cells',
                'stromal cells, nuclear', 'stromal cells, cytoplasmic'],
    "membranous and cytoplasmic": ['membranous, cytoplasmic', 'cytoplasmic/membrane',
                                   'mixed cytoplasmic and membranous'],
    "epithelial": ['epithelium', 'malignant epithelia', 'epithelial/cancer cells'],
    "nuclear and cytoplasmic": ['cytoplasmic, nuclear', 'nuclear, cytoplasmic',
                                'cytoplasmic and nuclear'],
    # "immune": ['intraepithelial', 'intra-epithelial',
    #            'intraepithelial tumor-infiltrating lymphocytes'],

    "vascular_endothelial": [
        "endothelial", "endothelium", "endothelial cells", "endothelial cell",
        "vessels", "blood vessels", "blood vessel", "microvessels", "microvessel",
        "vasculature", "vascular endothelial cells", "microvascular endothelium",
        "tumor vasculature",
    ],
    # "sex_cord_gonadal_stromal": [
    #     "granulosa cells", "sex cord cells", "sertoli cells", "leydig cells",
    #     "thecal cells", "theca cells", "luteinized stromal cells",
    #     "follicle cells", "foxl2-positive cells", "granulosa cell nucleus",
    # ],
    "germ_cells": ["germ cells", "oocytes"],
}

PATTERN_INTO_PD_NAN = ['tumor cells', 'tumor', 'tumour cells',
                       'cancer cells', 'all cells', 'cellular', 'tumoral cells',
                       'intra-tumoural', 'negative',

                       'tumoral', 'tumour', 'tumor cell', 'tumour cell', 'cancer',
                       'carcinoma cells', 'neoplastic cells', 'malignant cells',
                       'cancer tissue', 'tumorous']
# OLD
# PATTERN_VARIATIONS_DICT = {
#     "nuclear": ['nuclear', 'nucleus', 'tumour cells, nuclear'],
#     "membranous": ['membranous', 'membrane'],
#     "cytoplasmic": ['cytoplasmic', 'cytoplasm', 'tumour cells, cytoplasmic'],
#     "stromal": ['stromal', 'stroma', 'stromal cells', 'stromal cells, nuclear', 'stromal cells, cytoplasmic'],
#     "membranous and cytoplasmic": ['membranous, cytoplasmic', 'cytoplasmic/membrane',
#                                    'mixed cytoplasmic and membranous'],
#     "epithelial": ['epithelium', 'intraepithelial', 'malignant epithelia'],
#     "nuclear and cytoplasmic": ['cytoplasmic, nuclear', 'nuclear, cytoplasmic', 'cytoplasmic and nuclear']
# }
#
# PATTERN_INTO_PD_NAN = ['tumor cells', 'tumor', 'epithelial/cancer cells', 'tumour cells', 'cancer cells', 'all cells',
#                        'cellular', 'tumoral cells', 'intra-tumoural', 'negative']
