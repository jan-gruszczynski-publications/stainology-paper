# Dictionary for exact matching after cleaning the string (removing spaces, hyphens, etc.)
STAINS_VARIATIONS_DICTIONARY = {
    'alphasmoothmuscle': [
        'alphasmoothmuscleactin',
        'alphasmoothmuscleactin(sma)',
        'smoothmuscleactin',
        'alphasmoothmuscle'
    ],

    'ae1ae3': [
        'ae1/ae3',
        'ae1ae3',
        r'ae1/ae3 \(cytokeratin\)',
        'cytokeratin ae1/ae3',
        r'cytokeratin \(ae1/ae3\)',
        r'cytokeratin \(ae1/ae3\) \(antibody\)',
        r'cytokeratin ae1/ae3 \(antibody\)',
        'ae13',
        'ae1ae3',
        'ckae13',
        'cytokeratinae13',
        'cytokeratinae1ae3',
        'ae1ae3cytokeratins',
        'aeg1',
    ],
    'p53': ['tp53', 'p53'],
    'her2': ['her2neu', 'cerbb2', 'erbb2', 'her2'],
    'p16': ['p16ink4a', 'cdkn2a', 'p16'],
    'arid1a': ['baf250a', 'arid1a'],
    'smarca4': ['brg1', 'smarca4'],
    'braf': ['ve1', 'braf'],  # VE1 is the antibody for BRAF V600E mutation
    'met': ['cmet', 'met'],
    'cd117': ['ckit', 'cd117'],  # c-Kit is encoded by the KIT proto-oncogene

    # Hormone Receptors
    'er': ['estrogenreceptor', 'eralpha', 'erbeta', 'esr1', 'oestrogenreceptor', 'er'],
    'pr': ['progesteronereceptor', 'pgr', 'prb', 'pr'],

    # Cytokeratins
    'ck20': ['cytokeratin20', 'ck20'],
    'ck56': ['cytokeratin56', 'ck56'],
    'cytokeratin': ['ck', 'cytokeratin'],  # General cytokeratin group

    # Proliferation Markers
    # 'ki67': ['mib1ki67'],
    'cyclind1': ['cyclind1'],

    # Mismatch Repair (MMR) Proteins
    'mlh1': ['hmlh1', 'mlh1'],
    'msh2': ['hmsh2', 'msh2'],

    # Transcription Factors & Nuclear Proteins
    'hnf1b': ['hnf1beta', 'hnf1b'],
    'oct4': ['oct34', 'oct4'],
    'folr1': ['fralpha', 'folr1'],  # Folate Receptor Alpha

    # Cell Adhesion & Cytoskeleton
    'vimentin': ['vim', 'vimentin'],
    'ema': ['epithelialmembraneantigen', 'ema'],
    'gammacatenin': ['γcatenin', 'gammacatenin'],
    'claudin18': ['claudin18.2', 'cldn18', 'claudin18'],
    'cd44': ['cd44s', 'cd44v6', 'cd44'],
    'd240': ['podoplanin', 'd240'],

    # Other Markers
    'inhibin': ['inhibin', 'inhibinalpha', 'alphainhibin', 'inhibinantibody', 'alphasubunit', 'betaasubunit'],
    'vegf': ['vegf', 'vegfa', 'vegfc', 'vegfd'],
    'p27': ['p27', 'p27kip1'],
    'glypican3': ['glypican3', 'gpc3'],
    'amacr': ['amacr', 'amacrp504s'],  # Alpha-methylacyl-CoA racemase
    'lewisy': ['lewisy', 'lewisyantigen'],
    'mammaglobin': ['mammaglobinb'],
    'sstr': ['sstr', 'sst1', 'sst2a', 'sst3', 'sst4', 'sst5'],  # Somatostatin Receptors
    'napsin': ['napsin', 'napsina', 'napsin-a']
}

# Dictionary for regex matching on the string before major cleaning.
# This is useful for variations that include special characters or complex wording.
STAINS_VARIATIONS_DICTIONARY_FOR_REGEX = {
    'brca1': [
        'brca1',
        'brca1protein',
        r'brca1 \(protein\)',  # Note: parentheses are escaped for regex
        'brca1 protein',
    ],

}

EXPR_TYPE_VARIATIONS_DICT = {"over-expression": ["over-expression", 'overexpression'],
                             "increased": ["increased", "elevated"],
                             "normal": ["normal", "intact"],
                             "high": ["highexpression", "high", "highexpressed"],
                             "low": ["low", "low expression", "lowexpression", "low-expression"],
                             "decreased": ["decreased", "reduced", "underexpression",
                                           "reduced-expression", "reduced expression", "reduced expression"],
                             'negative': ['negative', 'negative expression']
                             }

PATTERN_VARIATIONS_DICT = {
    "nuclear": ['nuclear', 'nucleus', 'tumour cells, nuclear'],
    "membranous": ['membranous', 'membrane'],
    "cytoplasmic": ['cytoplasmic', 'cytoplasm', 'tumour cells, cytoplasmic'],
    "stromal": ['stromal', 'stroma', 'stromal cells', 'stromal cells, nuclear', 'stromal cells, cytoplasmic'],
    "membranous and cytoplasmic": ['membranous, cytoplasmic', 'cytoplasmic/membrane',
                                   'mixed cytoplasmic and membranous'],
    "epithelial": ['epithelium', 'endothelial', 'intraepithelial', 'malignant epithelia'],
    "nuclear and cytoplasmic": ['cytoplasmic, nuclear', 'nuclear, cytoplasmic', 'cytoplasmic and nuclear']
}

PATTERN_INTO_PD_NAN = ['tumor cells', 'tumor', 'epithelial/cancer cells', 'tumour cells', 'cancer cells', 'all cells',
                       'cellular', 'tumoral cells', 'intra-tumoural', 'negative']
