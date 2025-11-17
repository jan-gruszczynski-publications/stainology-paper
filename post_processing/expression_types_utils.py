import numpy as np
import pandas as pd
from pydantic import BaseModel

from post_processing.pipeline_utils import AbstractDFConverter


class FlipNegativeToPositive(BaseModel, AbstractDFConverter):
    total_N_col: str = 'total_N'
    expr_n_col: str = 'expr_n'
    expr_pct_col: str = 'expr_pct'
    expr_type_col: str = 'expr_type'

    from_type: str = 'negative'
    to_type: str = 'positive'
    expr_pct_equal_100: bool = False

    def __call__(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        print(f"Flipped from {self.from_type} to {self.to_type}", len(df[df[self.expr_type_col] == self.from_type]))
        df = df.copy(deep=True)

        for index, row in df.iterrows():
            if self.expr_pct_equal_100:

                if not bool(np.isclose(row[self.expr_pct_col], 100, atol=1e-5)):
                    continue

            if row[self.expr_type_col] == self.from_type:
                df.at[index, self.expr_type_col] = self.to_type
                df.at[index, self.expr_pct_col] = 100 - row[self.expr_pct_col]
                df.at[index, self.expr_n_col] = row[self.total_N_col] - row[self.expr_n_col]
        return df


class MapExpressionTypes(BaseModel, AbstractDFConverter):
    """
    Map negative expr_type to positive if expr_pct is 0.
    """
    key_words: list[str] = ['absent', 'loss']
    goal_expr_type: str = 'negative'

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy(deep=True)
        for key_word in self.key_words:
            df.expr_type = df.expr_type.str.replace(key_word, 'negative', case=False)
        return df
