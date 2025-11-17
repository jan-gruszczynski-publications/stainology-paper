import pandas as pd
from pydantic import BaseModel

from post_processing.pipeline_utils import AbstractDFConverter


class SelectPatternWithHighestExpr(BaseModel, AbstractDFConverter):
    key_columns: str = ["pattern"]
    value_columns: list[str] = ['expr_n', 'expr_pct']
    category_columns: list[str] = None

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy(deep=True)
        self.category_columns: list[str] = list(
            set(df.columns).difference(set(self.key_columns)).difference(set(self.value_columns)))
        # print(self.category_columns)

        output_rows = []
        total_original_rows = 0
        total_merged_rows = 0
        total_skipped_rows = 0
        for group_key, group_df in df.groupby(self.category_columns, dropna=False):
            if len(group_df) == 1:
                output_rows.append(group_df.iloc[0])
                continue
            expr_type = group_df['expr_type'].iloc[0]
            if expr_type == 'positive':
                agg_row = group_df.agg({
                    'expr_n': 'max',
                    'expr_pct': 'max',
                    # 'pattern': lambda x: ';'.join(x.unique())
                })
            elif expr_type == 'negative':
                agg_row = group_df.agg({
                    'expr_n': 'min',
                    'expr_pct': 'min',
                    # 'pattern': lambda x: ';'.join(x.unique())
                })
            else:
                total_skipped_rows += 1
                continue
            # pattern shoould be in form: expr_pct1 - pattern1; expr_pct2 - pattern2;...
            agg_row['pattern'] = ';'.join(
                f"{row['expr_pct']}-{row['pattern']}" for _, row in group_df.iterrows()
            )
            if isinstance(group_key, tuple):
                for col, val in zip(self.category_columns, group_key):
                    agg_row[col] = val
            else:
                agg_row[self.category_columns[0]] = group_key

            total_original_rows += len(group_df)
            total_merged_rows += 1
            output_rows.append(agg_row)
            # agg_df = agg_df#.reset_index(drop=False)
            # agg_df = agg_df.reset_index()
            # print(agg_df)
            # print(group_df['expr_pct'].idxmax())
            # highest_row = group_df.loc[group_df['expr_pct'].idxmax()]
            # print(highest_row)
        print(f"Total rows merged: {total_original_rows} into {total_merged_rows} rows.")
        print(f"Total rows skipped: {total_skipped_rows} rows.")

        #     max_expr_pct = group_df['expr_pct'].max()
        #     max_expr_pct_row = group_df[group_df['expr_pct'] == max_expr_pct].iloc[0]
        #     df.loc[group_df.index, 'pattern'] = max_expr_pct_row['pattern']
        return pd.DataFrame(output_rows).reset_index(drop=True)
