import numpy as np
import pandas as pd
from pydantic import BaseModel
from pydantic import Field

from post_processing.pipeline_utils import AbstractDFConverter


class FlipNegativeToPositive(BaseModel, AbstractDFConverter):
    total_N_col: str = 'total_N'
    expr_n_col: str = 'expr_n'
    expr_pct_col: str = 'expr_pct'
    expr_type_col: str = 'expr_type'

    from_type: str = 'negative'
    to_type: str = 'positive'
    expr_pct_equal_100: bool = False

    flip_info_cols: list[str] = Field(
        default_factory=lambda: ['expr_score', 'expr_intensity', 'expr_threshold']
    )
    flip_info_suffix: str = "(flipped neg->pos)"

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

                for col in self.flip_info_cols:
                    cell = row[col]
                    if pd.notna(cell):
                        df.at[index, col] = str(cell) + self.flip_info_suffix

        return df


class MapExpressionTypes(BaseModel, AbstractDFConverter):
    """
    Map expression types based on keywords in the 'expr_type' column. If a keyword is found, the expression type is replaced with the specified goal expression type.
    """
    key_words: list[str] = ['absent', 'loss']
    goal_expr_type: str = 'negative'

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy(deep=True)
        for key_word in self.key_words:
            df.expr_type = df.expr_type.str.replace(key_word, self.goal_expr_type, case=False)
        return df
