from typing import Literal

import pandas as pd
import plotly.io as pio
from pydantic import BaseModel
from pydantic import model_validator

from post_processing.pipeline_utils import AbstractDFConverter


class DropDuplicates(BaseModel, AbstractDFConverter):
    """
    A class to drop duplicates using column-specific tolerances.
    """
    ignore: set[str] = {"table_id", "PT", "total_N", "expr_n"}
    tolerance_cols: list[str] = ['expr_n', 'total_N']  # ['expr_pct', 'total_N', 'expr_n']
    absolute_tolerances: dict[str, float] = {
        # 'expr_pct': 3.0,
        'total_N': 2.0,
        'expr_n': 3.0
    }

    mode: Literal["largest_N", "largest_expr_pct", "drop_all"] = "largest"
    minimum_distance_for_largest_N: int = 10

    @model_validator(mode='after')
    def check_tolerances_defined(self) -> 'DropDuplicates':
        for col in self.tolerance_cols:
            if col not in self.absolute_tolerances:
                raise ValueError(f"Tolerance for column '{col}' is not defined in absolute_tolerances.")
        return self

    @staticmethod
    def remove_differing_by_only_table_id(df: pd.DataFrame) -> pd.DataFrame:
        before_shape = df.shape
        all_columns = set(df.columns.tolist())
        all_columns = list(all_columns.difference({'table_id'}))
        df = df.drop_duplicates(subset=all_columns, keep='first')
        print("Removed", before_shape[0] - df.shape[0], "rows that differed only by table_id.")
        return df

    def __call__(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df = df.copy(deep=True)
        df = self.remove_differing_by_only_table_id(df)

        df_shape_before = df.shape

        all_match_cols = set(df.columns.tolist()).difference(self.ignore)
        exact_match_cols = list(all_match_cols.difference(self.tolerance_cols))

        if exact_match_cols:
            df.sort_values(by=exact_match_cols, inplace=True)

        indices_to_keep = []
        problems_table_ids = []
        tolerances_series = pd.Series(self.absolute_tolerances)

        grouper = df.groupby(exact_match_cols, dropna=False) if exact_match_cols else [(None, df)]

        for _, group in grouper:
            if len(group) <= 1:
                indices_to_keep.extend(group.index.tolist())
                continue

            ranges = group[self.tolerance_cols].max() - group[self.tolerance_cols].min()
            is_close = (ranges <= tolerances_series[self.tolerance_cols]).all()

            if is_close:
                idx_to_keep = group['total_N'].idxmax()
                indices_to_keep.append(idx_to_keep)
                continue

            problems_table_ids.extend(group.table_id.unique().tolist())
            match self.mode:
                case "drop_all":
                    # If the rows differ more than the tolerance, drop all of them
                    indices_to_keep.extend([])

                case "largest_N":
                    sorted_group = group.sort_values(by='total_N', ascending=False)
                    largest_n = sorted_group.iloc[0]['total_N']
                    second_largest_n = sorted_group.iloc[1]['total_N']

                    if largest_n - second_largest_n >= self.minimum_distance_for_largest_N:
                        idx_to_keep = sorted_group.index[0]
                        indices_to_keep.append(idx_to_keep)
                        continue

                case "largest_expr_pct":
                    # if not abs(group.total_N.max() - group.total_N.min()) <= 3:
                    #     print(f"Varying total_N, investigate {group.iloc[0].table_id}")
                    #     print(group.total_N.unique())
                    #     print(group)
                    #     print("___")
                    #     continue

                    # Zapytać michała co robić w takiej sytuacji
                    idx_to_keep = group['expr_pct'].idxmax()
                    # print(group.loc[idx_to_keep].total_N)
                    if not group.loc[idx_to_keep].total_N > 10:
                        continue
                    indices_to_keep.append(idx_to_keep)

                case _:
                    raise ValueError(f"Unknown mode: {self.mode}. Use 'largest' or 'drop_all'.")

        df_after_tolerance_drop = df.loc[sorted(list(set(indices_to_keep)))].copy()

        print(
            f"Dropped {df_shape_before[0] - df_after_tolerance_drop.shape[0]} duplicates using tolerance logic, ignoring {self.ignore}.")
        print("Problems with duplicates:", len(list(set(problems_table_ids))))

        # return problems_table_ids, df_after_tolerance_drop
        return df_after_tolerance_drop