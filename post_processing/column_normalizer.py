import re
from typing import Dict, Any

import pandas as pd


GREEK_CHAR_TO_LATIN_NAME = {
    'α': 'alpha', 'Α': 'alpha',
    'β': 'beta', 'Β': 'beta',
    'γ': 'gamma', 'Γ': 'gamma',
    'δ': 'delta', 'Δ': 'delta',
    'ε': 'epsilon', 'Ε': 'Epsilon',
    'ζ': 'zeta', 'Ζ': 'Zeta',
    'η': 'eta', 'Η': 'Eta',
    'θ': 'theta', 'Θ': 'Theta',
    'ι': 'iota', 'Ι': 'Iota',
    'κ': 'kappa', 'Κ': 'Kappa',
    'λ': 'lambda', 'Λ': 'Lambda',
    'μ': 'mu', 'Μ': 'Mu',
    'ν': 'nu', 'Ν': 'Nu',
    'ξ': 'xi', 'Ξ': 'Xi',
    'ο': 'omicron', 'Ο': 'Omicron',
    'π': 'pi', 'Π': 'Pi',
    'ρ': 'rho', 'Ρ': 'Rho',
    'σ': 'sigma', 'Σ': 'Sigma',
    'τ': 'tau', 'Τ': 'Tau',
    'υ': 'upsilon', 'Υ': 'Upsilon',
    'φ': 'phi', 'Φ': 'Phi',
    'χ': 'chi', 'Χ': 'Chi',
    'ψ': 'psi', 'Ψ': 'Psi',
    'ω': 'omega', 'Ω': 'Omega',
}


def generate_variations(s: str) -> list[str]:
    """
    Generates a list of variations for a given string.

    This includes:
    1.  Replacing Greek characters (α, β) with Latin names (alpha, beta).
    2.  Adding/removing separators (dashes, spaces) between letters and digits.
    3.  Swapping existing dashes and spaces.
    4.  Providing a "cleaned" version with no separators.
    """
    # Use a set to automatically handle duplicate variations.
    variations = {s}

    # --- 1. Generate Latin Name Variations from Greek Chars ---
    # Create a new variation if any Greek characters are found and replaced.
    text_with_latin_names = s
    changed = False
    for greek, latin in GREEK_CHAR_TO_LATIN_NAME.items():
        if greek in text_with_latin_names:
            text_with_latin_names = text_with_latin_names.replace(greek, latin)
            changed = True

    if changed:
        variations.add(text_with_latin_names)

    # --- 2. Generate Separator Variations ---
    # This logic is applied to all base variations (original and the one with Latin names).
    for variation in list(variations):
        # Create a "cleaned" version by removing dashes and spaces.
        cleaned = variation.replace('-', '').replace(' ', '')
        variations.add(cleaned)

        # From the cleaned string, add variations with separators at boundaries.
        # Boundary: Non-Digit to Digit (\D\d)
        if re.search(r'(\D)(\d)', cleaned):
            variations.add(re.sub(r'(\D)(\d)', r'\1-\2', cleaned))
            variations.add(re.sub(r'(\D)(\d)', r'\1 \2', cleaned))

        # Boundary: Digit to Non-Digit (\d\D)
        if re.search(r'(\d)(\D)', cleaned):
            variations.add(re.sub(r'(\d)(\D)', r'\1-\2', cleaned))
            variations.add(re.sub(r'(\d)(\D)', r'\1 \2', cleaned))

        # Handle swapping existing separators in the original variation.
        if ' ' in variation:
            variations.add(variation.replace(' ', '-'))
        if '-' in variation:
            variations.add(variation.replace('-', ' '))

    return sorted(list(variations))


class ColumnNormalizer:
    """
    A callable class to normalize stain names in a pandas DataFrame column.
    This version integrates a sophisticated `generate_variations` function.
    """

    def __init__(self,
                 variations_dict: Dict[str, Any] = None,
                 regex_variations_dict: Dict[str, Any] = None,
                 key_column: str = 'stain'):
        """
        Initializes the normalizer and creates a reversed dictionary for fast lookups.
        """
        self.key_column: str = key_column
        self.variations_dict = {} if variations_dict is None else variations_dict
        self.regex_variations_dict = {} if regex_variations_dict is None else regex_variations_dict

        # Create a reversed "flat" dictionary for O(1) lookups.
        # Maps 'alphasmoothmuscleactin' -> 'alphasma'
        self.reversed_variations_dict = {}
        for key, variations_list in self.variations_dict.items():
            for variation in variations_list:
                self.reversed_variations_dict[variation.lower()] = key

    def _normalize_value(self, value: Any) -> Any:
        """
        Applies the full normalization logic to a single value.
        """
        if pd.isnull(value):
            return value

        # --- Step 1: Pre-processing and '+' handling ---
        proc_str = str(value).strip()
        if '+' in proc_str:
            proc_str = re.sub(r'\(.*?\)', '', proc_str)
            proc_str = proc_str.split('+', 1)[0].strip()

        proc_str_lower = proc_str.lower()

        # --- Step 2: Regex-based dictionary lookup (high priority) ---
        for key, patterns in self.regex_variations_dict.items():
            for pattern in patterns:
                if re.search(pattern, proc_str_lower):
                    return key

        # --- Step 3: Generate all variations using the advanced function ---
        all_variations = generate_variations(proc_str)
        # print(all_variations)
        # --- Step 4: Check all generated variations against the dictionary ---
        for var in all_variations:
            if var in self.reversed_variations_dict:
                return self.reversed_variations_dict[var]

        # --- Step 5: Fallback ---
        # If no mapping found, return the most "cleaned" version.
        return re.sub(r'[\s\-/()]', '', proc_str_lower)

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes the normalization on a DataFrame.
        """
        df = df.copy(deep=True)
        if self.key_column not in df.columns:
            raise ValueError(f"Column '{self.key_column}' not found in the DataFrame.")

        if f'{self.key_column}_old' not in df.columns:
            df[f'{self.key_column}_old'] = df[self.key_column]

        # df[self.key_column] = df[self.key_column].str.replace("β", "beta")
        # df[self.key_column] = df[self.key_column].str.replace("α", "alpha")
        df[self.key_column] = df[self.key_column].apply(self._normalize_value)
        return df


class SimplifiedColumnNormalizer:
    """
    A callable class to normalize text pattern values in a pandas DataFrame column.
    This version uses a simplified, direct lookup method suitable for text phrases.
    """

    def __init__(self,
                 variations_dict: Dict[str, Any],
                 key_column: str = 'pattern'):
        """
        Initializes the normalizer and creates a reversed dictionary for fast lookups.
        """
        self.key_column: str = key_column
        self.variations_dict = variations_dict

        # Create a reversed "flat" dictionary for O(1) lookups.
        # It maps a cleaned variation like 'membranous, cytoplasmic' to 'membranous and cytoplasmic'.
        self.reversed_variations_dict = {}
        for key, variations_list in self.variations_dict.items():
            for variation in variations_list:
                # Clean the variation for robust matching
                cleaned_variation = self._preprocess_string(variation)
                self.reversed_variations_dict[cleaned_variation] = key

    def _preprocess_string(self, value: str) -> str:
        """Standard cleaning for strings: lowercase, strip whitespace, and normalize separators."""
        if not isinstance(value, str):
            return ""
        # Replace common separators like commas and slashes with a space, then strip and lowercase.
        s = re.sub(r'[,/]', ' ', value)
        # Condense multiple spaces into one
        s = re.sub(r'\s+', ' ', s).strip().lower()
        return s

    def _normalize_value(self, value: Any) -> Any:
        """Applies the normalization logic to a single value."""
        if pd.isnull(value):
            return value

        # Pre-process the input string in the same way as the dictionary keys
        cleaned_value = self._preprocess_string(str(value))

        # Direct lookup in the reversed dictionary
        return self.reversed_variations_dict.get(cleaned_value, cleaned_value)

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        """Executes the normalization on a DataFrame."""
        df = df.copy(deep=True)
        if self.key_column not in df.columns:
            raise ValueError(f"Column '{self.key_column}' not found in the DataFrame.")

        if f'{self.key_column}_old' not in df.columns:
            df[f'{self.key_column}_old'] = df[self.key_column]

        # Apply the simplified normalization function
        df[self.key_column] = df[self.key_column].apply(self._normalize_value)
        return df
