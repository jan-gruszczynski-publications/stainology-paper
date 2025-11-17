from itertools import combinations

import pandas as pd
from pydantic import BaseModel

from post_processing.droppers import DropRowsWithValuesInColumn
from post_processing.pipeline_utils import AbstractDFConverter
from post_processing.remover_utils import remove_tables_from_df


class RemoveIntraInconsistent(BaseModel, AbstractDFConverter):
    tolerance: float = 0
    do_remove: bool = True
    # category_columns: list[str] = [
    #     'tumour',
    #     'stain',
    #     'expr_type',
    #     'pattern',
    #     'expr_distribution', 'expr_intensity', 'expr_threshold',
    #     'expr_score', 'group', 'group_cat', 'notes'
    # ]
    ignore_columns: list[str] = []
    category_columns: list[str] = []
    name: str = "intra_inconsistent"
    value_columns: list[str] = [
        'total_N',
        'expr_n',
        'expr_pct',
    ]
    key_columns: list[str] = [
        'expr_pct'
    ]

    def __call__(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df = df.copy(deep=True)

        self.category_columns: list[str] = list(
            set(df.columns).difference(set(self.ignore_columns)).difference(set(self.value_columns)))
        diff_df = []
        inconsistent_indices = []
        suspected_wrong_name_match = []
        for PMID in df.PMID.unique():

            one_paper = df[df.PMID == PMID].copy()  #.reset_index(drop=True)
            # print(one_paper)
            # one_paper.table_id = one_paper.table_id.fillna('abstract')
            # print(one_paper.groupby(['matched_tumour', 'stain', 'expr_type', 'pattern']).groups)
            # print(self.category_columns)
            # print(one_paper.groupby(self.category_columns).mean(numeric_only=True))
            for group_key, group_df in one_paper.groupby(self.category_columns, dropna=False):

                # print(group_key)
                if len(group_df) == 1:
                    # print("Skipping group with one element")
                    continue

                for idx_a, idx_b in combinations(group_df.index, 2):
                    a, b = group_df.loc[idx_a], group_df.loc[idx_b]
                    if a.equals(b):
                        # print("equal")
                        continue

                    # if any(pd.isna(a[col]) or pd.isna(b[col]) for col in self.value_columns):
                    #     print("NaN in values")
                    #     continue

                    if any(abs(a[col] - b[col]) <= self.tolerance for col in self.key_columns):
                        # print("Too small difference")
                        continue

                    # Do wszystkiego
                    if a['tumour'] != b['tumour']:
                        suspected_wrong_name_match.extend([a, b, pd.Series()])
                        continue

                    if not a[self.value_columns].equals(b[self.value_columns]):
                        # if a['cancer_name'] == b['cancer_name'] and a['table_id'] == b['table_id']:
                        #     continue
                        # messed_up.extend([a.reset_index().columns[1], b.reset_index().columns[1]])
                        diff_df.extend([a, b, pd.Series()])
                        inconsistent_indices.extend([idx_a, idx_b])
                    # break
        assert len(diff_df) / 3 * 2 == len(inconsistent_indices)
        print("Intra inconsistent:", len(inconsistent_indices), "Set:", len(set(inconsistent_indices)))
        print(self.name)
        self.singleton.my_dict[self.name] = pd.DataFrame(diff_df)
        self.singleton.my_dict['suspected_wrong_name_match'] = pd.DataFrame(suspected_wrong_name_match)
        # if self.do_remove:
        #     df = df.drop(index=list(set(inconsistent_indices)))
        return df


class RemoveInterInconsistent(BaseModel, AbstractDFConverter):
    tolerance: float = 10
    do_remove: bool = True
    category_columns: list[str] = [
        'matched_tumour',
        'stain',
        'expr_type',
        'pattern',
    ]

    total_N_col: str = 'total_N'
    expr_n_col: str = 'expr_n'
    expr_pct_col: str = 'expr_pct'

    def __call__(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        big_diff = []
        inconsistent_indices = []

        grouped = df.groupby(self.category_columns, dropna=False)
        for group_key, group_df in grouped:
            if len(group_df) == 1:
                continue
            for idx_a, idx_b in combinations(group_df.index, 2):
                a, b = group_df.loc[idx_a], group_df.loc[idx_b]
                if a.PMID == b.PMID:
                    continue
                abs_diff = abs(a[self.expr_pct_col] - b[self.expr_pct_col])
                # print(abs_diff)
                if abs_diff > self.tolerance and a[self.total_N_col] > 8 and b[self.total_N_col] > 8:
                    big_diff.extend([a, b, pd.Series()])
                    inconsistent_indices.extend([idx_a, idx_b])

        self.singleton.my_dict['inter_inconsistent'] = pd.DataFrame(big_diff)
        assert len(big_diff) / 3 * 2 == len(inconsistent_indices)
        print("Inter inconsistent:", len(inconsistent_indices), "Set:", len(set(inconsistent_indices)))
        if self.do_remove:
            df = df.drop(index=list(set(inconsistent_indices)))
        # df = df.drop(index=list(set(inconsistent_indices)))
        return df



class IdentifyMultipleStudyTables(BaseModel, AbstractDFConverter):
    category_columns: list[str] = [
        'tumour',
        'stain_old',
        'expr_type',
        'pattern',
        'expr_threshold',
        'expr_distribution',
        'expr_intensity',
        'expr_score',
        'group',
        'group_cat',
        # 'notes'
    ]
    multiple_studies_key_words: list[str] = ['et al.', 'study']
    value_columns: list[str] = [
        'total_N',
        'expr_n',
        'expr_pct',
    ]

    key_columns: list[str] = [
        'expr_pct'
    ]

    tolerance: int = 0
    min_counter: int = 1
    min_unique_total_N: int = 3
    drop_multiple_study_tables: bool = True
    drop_patient_tables: bool = True

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df_backup = df.copy(deep=True)

        multiple_study_tables = []
        patient_tables = []
        for table_id in df.table_id.unique():
            if "abstract" in table_id:
                continue
            one_table = df[df.table_id == table_id].copy()

            finder = DropRowsWithValuesInColumn(column='notes', values=self.multiple_studies_key_words)
            have_keywords_mask = finder.find_mask(one_table)
            if have_keywords_mask.any():
                multiple_study_tables.append(table_id)
                continue

            counter = 0
            for group_key, group_df in one_table.groupby(self.category_columns, dropna=False):

                if not len(group_df) >= self.min_unique_total_N:
                    continue
                # print(group_df)
                unique_total_N_count = len(group_df['total_N'].unique())
                if unique_total_N_count >= self.min_unique_total_N:
                    if unique_total_N_count > 12:
                        patient_tables.append(table_id)
                    # else:
                    #     counter += 1
                    continue

                unique_expr_pct = len(group_df['expr_pct'].unique())
                if unique_expr_pct >= self.min_unique_total_N:
                    if unique_expr_pct > 12:
                        patient_tables.append(table_id)
                    # else:
                    #     counter += 1
                    continue

                unique_expr_n = len(group_df['expr_n'].unique())
                if unique_expr_n >= self.min_unique_total_N:
                    if unique_expr_n > 12:
                        patient_tables.append(table_id)
                    # else:
                    #     counter += 1
                    continue
            if counter >= self.min_counter:
                multiple_study_tables.append(table_id)
        print("Multiple study tables:", len(set(multiple_study_tables)))
        print("Patient tables:", len(set(patient_tables)))
        self.singleton.my_dict['multiple_study_tables'] = list(set(multiple_study_tables))
        self.singleton.my_dict['patient_tables'] = list(set(patient_tables))

        if self.drop_multiple_study_tables:
            df_backup = remove_tables_from_df(df_backup, multiple_study_tables)
        if self.drop_patient_tables:
            df_backup = remove_tables_from_df(df_backup, patient_tables)

        return df_backup