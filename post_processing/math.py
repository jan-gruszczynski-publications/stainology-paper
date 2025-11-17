import pandas as pd
from pydantic import BaseModel

from post_processing.pipeline_utils import AbstractDFConverter
from post_processing.remover_utils import remove_all_pairs_with_the_same_stain_and_tumour_by_table_id


class CalculateExprPctAgain(BaseModel, AbstractDFConverter):
    expr_pct_col: str = "expr_pct"

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy(deep=True)
        df[self.expr_pct_col] = df['expr_n'] / df['total_N'] * 100
        df[self.expr_pct_col] = df[self.expr_pct_col].round(2)
        return df


class CalculateMissingValues(BaseModel, AbstractDFConverter):
    total_N_col: str = 'total_N'
    expr_n_col: str = 'expr_n'
    expr_pct_col: str = 'expr_pct'

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy(deep=True)
        df = df.astype({self.total_N_col: float, self.expr_n_col: float, self.expr_pct_col: float})
        missing_indexes = []
        for index, row in df.iterrows():
            total = row[self.total_N_col]
            samples = row[self.expr_n_col]
            percentage = row[self.expr_pct_col]

            if pd.isna(samples) and pd.notna(total) and pd.notna(percentage):
                df.at[index, self.expr_n_col] = (percentage / 100) * total
                missing_indexes.append(index)
            elif pd.isna(percentage) and pd.notna(samples) and pd.notna(total):
                if total <= 0:
                    continue
                df.at[index, self.expr_pct_col] = (samples / total) * 100
                missing_indexes.append(index)
            elif pd.isna(total) and pd.notna(samples) and pd.notna(percentage):
                if percentage <= 0:
                    continue
                df.at[index, self.total_N_col] = (samples / percentage) * 100
                missing_indexes.append(index)
        df[self.expr_pct_col] = df[self.expr_pct_col].round(2)
        df[self.expr_n_col] = df[self.expr_n_col].round(0)
        df[self.total_N_col] = df[self.total_N_col].round(0)
        print("Calculated values for:", len(missing_indexes))
        return df


class RemoveMathConsistent(BaseModel, AbstractDFConverter):
    tolerance: float

    total_N_col: str = 'total_N'
    expr_n_col: str = 'expr_n'
    expr_pct_col: str = 'expr_pct'
    remove_all_pairs: bool = True

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Check consistency between numerical values and percentages in the dataset.

        Args:
            df (pd.DataFrame): Input DataFrame with columns 'total_samples[n]',
                              'samples_with_expression_type[n]', and 'samples_with_expression_type[%]'
            tolerance (float): Acceptable difference between calculated and actual values (default: 0.01)

        Returns:
            list: List of row indices where inconsistencies were found
        """
        inconsistent_indices = []

        for index, row in df.iterrows():
            total = row[self.total_N_col]
            samples = row[self.expr_n_col]
            percentage = row[self.expr_pct_col]
            if pd.notna(total) and total <= 0:
                inconsistent_indices.append(index)
                continue
            if pd.notna(samples) and samples < 0:
                inconsistent_indices.append(index)
                continue
            if pd.notna(percentage) and percentage < 0:
                inconsistent_indices.append(index)
                continue

            # Case 1: Check if total samples and samples with expression are present
            if pd.notna(total) and pd.notna(samples):
                calculated_percentage = (samples / total) * 100
                if pd.notna(percentage):
                    if abs(calculated_percentage - percentage) > self.tolerance:
                        # print('Pmid:', row['PMID'])
                        # print("Percentage inconsistent:", abs(calculated_percentage - percentage))

                        inconsistent_indices.append(index)

            # Case 2: Check if total samples and percentage are present
            if pd.notna(total) and pd.notna(percentage):
                calculated_samples = (percentage / 100) * total
                if pd.notna(samples):
                    if abs(calculated_samples - samples) > self.tolerance:
                        # print('Pmid:', row['PMID'])
                        # print("Samples inconsistent:", abs(calculated_samples - samples))
                        inconsistent_indices.append(index)

            # Case 3: Check if samples and percentage are present
            if pd.notna(samples) and pd.notna(percentage):
                if percentage == 0:
                    continue
                calculated_total = (samples / (percentage / 100))
                if pd.notna(total):
                    if abs(calculated_total - total) > self.tolerance:
                        # print('Pmid:', row['PMID'])
                        # print("Total inconsistent:", abs(calculated_total - total))
                        inconsistent_indices.append(index)

        indexes = sorted(list(set(inconsistent_indices)))
        # print(max(indexes), min(indexes))
        # print(max(df.index.tolist()), min(df.index.tolist()))
        # valid_indices = sorted(list(set(inconsistent_indices).intersection(df.index)))
        # print(len(valid_indices), len(indexes))
        # print(indexes)
        self.singleton.my_dict['math_showed_wrong'] = df.iloc[indexes]
        print("Math inconsistent:", len(indexes))
        if not self.remove_all_pairs:
            df = df.drop(indexes)
        else:
            df = remove_all_pairs_with_the_same_stain_and_tumour_by_table_id(df, indexes)
        return df
