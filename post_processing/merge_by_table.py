from itertools import combinations
from typing import Union

import pandas as pd
from pydantic import BaseModel

from post_processing.pipeline_utils import AbstractDFConverter
from post_processing.remover_utils import remove_tables_from_df


class RemoveNegativeDuplicates(BaseModel, AbstractDFConverter):
    category_columns: list[str] = ['tumour', 'stain', 'pattern',
                                   'expr_distribution',
                                   'expr_threshold',
                                   'expr_intensity', 'expr_score', 'notes']

    value_columns: list[str] = [
        'total_N',
        'expr_n',
        'expr_pct',
    ]

    do_remove: bool = True
    log: bool = True

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy(deep=True)
        duplicates_indexes = []
        duplicates_pairs = []
        for PMID in df.PMID.unique():
            one_paper = df[df.PMID == f"{PMID}"].copy()
            one_paper = one_paper.dropna(subset=self.value_columns, axis='rows')

            indexes_to_drop = []
            for group_key, group_df in one_paper.groupby(self.category_columns, dropna=False):
                if len(group_df) == 1:
                    continue

                counter = 0
                for idx_a, idx_b in combinations(group_df.index, 2):
                    a, b = group_df.loc[idx_a], group_df.loc[idx_b]
                    if a.expr_type == 'positive' and b.expr_type == 'negative':
                        a, b = b, a
                        idx_a, idx_b = idx_b, idx_a
                    if a.expr_type == 'negative' and b.expr_type == 'positive':
                        if a.total_N == b.total_N and (b.total_N - b.expr_n) == a.expr_n:
                            duplicates_pairs.extend([a, b, pd.Series()])
                            indexes_to_drop.append(idx_a)
                            counter += 1
            duplicates_indexes.extend(indexes_to_drop)
        if self.log:
            print("Negative duplicates:", len(duplicates_indexes), "Set:", len(set(duplicates_indexes)))
            self.singleton.my_dict['negative_duplicates'] = pd.DataFrame(duplicates_pairs)
        if self.do_remove:
            df = df.drop(index=list(set(duplicates_indexes)))
        return df

    # RemoveInConsistent3()(concat.copy())


class MergeDifferingByColumns(BaseModel, AbstractDFConverter):
    # merge ignoring
    differing_columns: list[str] = ['expr_score', 'expr_intensity', 'expr_threshold', 'expr_distribution']

    # map_by: str = 'expr_score'  # merge by this column
    value_columns: list[str] = ['total_N', 'expr_n', 'expr_pct']

    category_columns: list[str] = None

    tables_to_drop: list[str] = []
    unique_errors: list[str] = []

    def _merge_rows_with_positive_exp_score(self, group_df: pd.DataFrame) -> pd.DataFrame | Union[int] | list[int]:
        group_df = group_df.copy(deep=True)

        # apply_mapping = lambda x: self.mapping.get(x, "unmapped")
        # group_df[f'{self.map_by}_mapped'] = group_df[self.map_by].apply(apply_mapping)
        # if 'unmapped' in group_df[f'{self.map_by}_mapped'].unique():  # Were not able to map all scores
        #     print(f"Unmapped expr_score found, investigate {group_df.iloc[0].PMID} {group_df.iloc[0].table_id}")
        #     return group_df, None, group_df.index.tolist()
        # print(group_df['total_N'].unique())
        if len(group_df['total_N'].unique()) != 1:
            self.tables_to_drop.append(group_df.iloc[0].table_id)
            # print(f"Varying total_N, investigate {group_df.iloc[0].table_id}")
            self.unique_errors.append(f"Varying total_N, investigate {group_df.iloc[0].table_id}")

        # 21457161_page_5_table_0 -> take the first rows with all nans if available (instead of scores merging)
        only_differing_columns = group_df[self.differing_columns]
        all_nan_rows = only_differing_columns[only_differing_columns.isna().all(axis=1)]
        if all_nan_rows.shape[0] > 1:
            self.tables_to_drop.append(group_df.iloc[0].table_id)
            # print(f"More than one row with all NaN in differing columns, investigate: {group_df.iloc[0].table_id}")
            self.unique_errors.append(
                f"More than one row with all NaN in differing columns, investigate: {group_df.iloc[0].table_id}"
            )
        if all_nan_rows.shape[0] > 0:
            nan_index = all_nan_rows.index[0]
            group_df_index = group_df.index.tolist()
            group_df_index.remove(nan_index)
            return group_df.loc[nan_index], nan_index, group_df_index

        first_index = group_df.index[0]
        indexes_to_drop = group_df.index[1:].tolist()

        aggregated = group_df.iloc[0][self.category_columns + ['PMID', 'table_id']].to_dict()
        _differing_columns = [col for col in self.differing_columns if col not in ('PMID', 'table_id')]
        aggregated.update({
            'total_N': group_df['total_N'].iloc[0],
            'expr_n': group_df['expr_n'].sum(),
            **{
                merged_column: 'MRD: ' + ';'.join(group_df[merged_column].astype(str))
                for merged_column in _differing_columns
            },
        })
        if aggregated['total_N'] == 0:
            self.tables_to_drop.append(group_df.iloc[0].table_id)
            self.unique_errors.append(f"Total N is NA:, investigate {group_df.iloc[0].table_id}")
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            aggregated['expr_pct'] = aggregated['expr_n'] / aggregated['total_N'] * 100

        if aggregated['expr_n'] > aggregated['total_N']:
            self.tables_to_drop.append(group_df.iloc[0].table_id)
            # print(f"expr_n > total_N in {group_df.iloc[0].PMID} {group_df.iloc[0].table_id}")
            self.unique_errors.append(
                f"expr_n > total_N in {group_df.iloc[0].PMID} {group_df.iloc[0].table_id}"
            )
            # return group_df, None, group_df.index.tolist()

        return pd.Series(aggregated), first_index, indexes_to_drop

    def _take_negative_if_possible(self, group_df: pd.DataFrame):
        group_df = group_df.copy(deep=True)

        only_differing_columns = group_df[self.differing_columns]
        all_nan_rows = only_differing_columns[only_differing_columns.isna().all(axis=1)]
        if all_nan_rows.shape[0] > 0:
            nan_index = all_nan_rows.index[0]
            group_df_index = group_df.index.tolist()
            group_df_index.remove(nan_index)
            return group_df.loc[nan_index], nan_index, group_df_index

        negative_rows = group_df[group_df.expr_type == 'negative']
        # negative_rows = ConditionalOverWrite(
        #         conditions=[{
        #             'cond_field': ['expr_score', 'expr_type'],
        #             'cond': lambda expr_score, expr_type: pd.isna(expr_score) and expr_type == 'negative',
        #             'res_field': 'expr_score',
        #             'res_value': 0
        #         }]
        #     )(negative_rows)
        # print(negative_rows)
        # negative_rows = negative_rows.drop_duplicates()
        # print(negative_rows.shape)
        # raise IndexError

        if negative_rows.shape[0] > 2:
            # print(f"More than two negative rows, skipping: {group_df.iloc[0].table_id}")
            self.unique_errors.append(f"More than two negative rows, skipping: {group_df.iloc[0].table_id}")
            self.tables_to_drop.append(group_df.iloc[0].table_id)
            return None, None, []
        if negative_rows.shape[0] > 1:
            # print(f"More than one negative rows, investigate: {group_df.iloc[0].table_id}")
            self.unique_errors.append(f"More than one negative rows, investigate: {group_df.iloc[0].table_id}")
            self.tables_to_drop.append(group_df.iloc[0].table_id)
            return None, None, []
        if negative_rows.shape[0] == 1:
            neg_row_index = negative_rows.index[0]
            group_df_index = group_df.index.tolist()
            group_df_index.remove(neg_row_index)
            return group_df.loc[neg_row_index], neg_row_index, group_df_index
        return None, None, []

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy(deep=True)
        self.category_columns: list[str] = list(
            set(df.columns).difference(set(self.differing_columns)).difference(set(self.value_columns)))
        dropped_indexes_num = 0

        indexes_to_drop: list[int] = []
        for table_id in df.table_id.unique():
            one_table = df[df.table_id == table_id].copy()
            # print(one_table.shape)
            # one_table = one_table.dropna(subset=self.value_columns, axis='rows')
            # print(one_table.shape)
            # Check if it is possible to take negative
            _indexes_to_drop: list[int] = []
            category_columns_without_expr_type = [cat for cat in self.category_columns if cat != 'expr_type']
            for group_key, group_df in one_table.groupby(category_columns_without_expr_type, dropna=False):
                # print(group_df)
                if len(group_df) == 1:
                    # print(group_df.shape)
                    # print(group_df)
                    continue

                # raise
                # print(group_df)
                neg_row, row_idx, not_negative_indexes_to_drop = self._take_negative_if_possible(group_df)
                # print(not_negative_indexes_to_drop)
                if row_idx:
                    df.loc[row_idx] = neg_row
                _indexes_to_drop.extend(not_negative_indexes_to_drop)
                dropped_indexes_num += len(not_negative_indexes_to_drop)
            # print(_indexes_to_drop)
            one_table = one_table.drop(_indexes_to_drop)
            indexes_to_drop.extend(_indexes_to_drop)
            # print(one_table.shape)

            for group_key, group_df in one_table.groupby(self.category_columns, dropna=False):
                if len(group_df) == 1:
                    # print(group_df)
                    continue
                # print(group_df.shape)
                # break
                # if there are non nans in expr_score columns:
                # if not group_df['expr_score'].isna().any():
                merged_row, row_idx, merged_indexes_to_drop = self._merge_rows_with_positive_exp_score(group_df)
                if row_idx:
                    df.loc[row_idx] = merged_row
                indexes_to_drop.extend(merged_indexes_to_drop)
                dropped_indexes_num += len(merged_indexes_to_drop)

        df = df.drop(indexes_to_drop)
        neg_duplicates_remover = RemoveNegativeDuplicates(
            category_columns=['tumour', 'stain'],
            log=False
        )
        df = neg_duplicates_remover(df.copy())
        return df


class MergeDifferingByColumnsPerTableID(BaseModel, AbstractDFConverter):
    do_remove: bool = True

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy(deep=True)

        merger = MergeDifferingByColumns()
        merger.tables_to_drop = []
        merger.unique_errors = []

        merged_tables = []
        for table_id in df.table_id.unique():
            one_table = df[df.table_id == table_id].copy()
            # one_table = one_table.dropna(subset=merger.value_columns, axis='rows')
            merged_table = merger(one_table)
            merged_tables.append(merged_table)
            # df.loc[df.table_id == merged_table.table_id] = merged_table
        df = pd.concat(merged_tables)
        self.singleton.my_dict['dropped_differing'] = list(set(merger.tables_to_drop))

        for error in set(merger.unique_errors):
            print(error)

        if self.do_remove:
            return remove_tables_from_df(df, merger.tables_to_drop)
        else:
            return df
