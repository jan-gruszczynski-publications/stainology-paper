from itertools import combinations

import numpy as np
import pandas as pd


class CleanColumn:
    def __call__(self, column: pd.Series) -> pd.Series:
        cleaned = column.astype(str)
        cleaned[column.isna()] = np.nan
        return (
            cleaned.str.lower()
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True)
            .str.strip()
        )


class MergeDifferingByOnlyOneSign:

    def __init__(self, sign: str = '-'):
        self.sign: str = sign

    def _check_if_differ_only_by_one_sign(self, a: str, b: str) -> bool:
        a, b = a.replace(self.sign, ''), b.replace(self.sign, '')
        a, b = a.strip(), b.strip()
        if len(a) != len(b):
            return False
        return a == b

    def __call__(self, column: pd.Series) -> pd.Series:
        column = column.copy()
        unique_values = column.unique().tolist()
        pairs = list(combinations(unique_values, 2))
        differ_by_one = []
        for a, b in pairs:
            if self._check_if_differ_only_by_one_sign(a, b):
                differ_by_one.append((a, b))
        for a, b in differ_by_one:
            column = column.str.replace(a, b)
        return column
