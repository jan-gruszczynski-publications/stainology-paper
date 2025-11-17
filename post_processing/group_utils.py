from typing import Literal
from typing import Union

import pandas as pd
from pydantic import BaseModel

from post_processing.droppers import DropRowsWithValuesInColumn
from post_processing.pipeline_utils import AbstractDFConverter


class SelectHistologicalGroupFromTable(BaseModel, AbstractDFConverter):
    inclusion_key_words: list[str] = ['type', 'histology', 'tumour', 'histologic',
                                      'primary carcinoma', 'histologic assessment of ovarian origin',
                                      'histotype', 'classification', 'tumor', 'cohort', 'carcinoma',
                                      'morphological specifics', 'histopathologic cell type', 'benign',
                                      'low malignant potential', 'primary ovarian neoplasms', 'metastases to the ovary',
                                      'diagnosis', 'diagnostic category', 'category']

    inclusion_multiple_key_words: list[str] = ["malignant", "carcinoma", "histology", "histological types",
                                               "ovarian adenocarcinomas",
                                               "histotype", "histological type", "histologic", "pathologic type",
                                               "pathologic subtypes", "pathological type",
                                               "subtype", "tumor histological type", "histological subtype",
                                               "pathological subtypes",
                                               "subtype", "serous carcinoma", 'epithelial tumor',
                                               'sex cord-stromal tumor', 'germ cell tumor',
                                               'metastatic tumor', 'histologic subtype', 'histology subtype',
                                               'histologic subtype', 'histological type',
                                               'subtype', 'pathological type', 'the pathology types',
                                               'histologic subtype', 'histological type', 'pathological type',
                                               'histological subtype', 'histologic type', 'histological subtype',
                                               'pathology type', 'histology type',
                                               'benign tumors', 'borderline tumors']

    exclusion_key_words: list[str] = ['grade', 'residual', 'grading', 'size', 'tumor characteristics', 'stage',
                                      'component', 'effusions', 'diagnosis stage', 'stage', 'grade',
                                      "age at", "localization", "percentage", "surgery type", "emt phenotype",
                                      "tumor behavior",
                                      "primary tumour origin and cldn18 status", "tumour area", "genotype",
                                      "tumor diameter",
                                      "tumor response", "analysis type", "age of", "phenotype", "endometriosis type",
                                      "intensity category",
                                      "tp53 mutation type", "genotype", "tumour status", "carcinomatosis", "diameter",
                                      "tp53", "in tumor cells score",
                                      "ascites with tumor cells", "p53 mutation type",
                                      "reductase type 1 immunoreactivity", "six1 intratumoral stromal expression",
                                      "braf mutation types", "chemoresponse at diagnosis", "test type",
                                      "survival analysis type", "position of tumors", "her2 status classification",
                                      "days to new tumor event", "depth", "tumor proportion score",
                                      "malignant tumor cells in ascites", "laterality", 'growth pattern']

    tables_to_drop: list[str] = []
    no_groups: list[str] = []

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        self.tables_to_drop = []
        self.no_groups = []

        df = df.copy(deep=True)
        inclusion_keywords_finder = DropRowsWithValuesInColumn(column='group', values=self.inclusion_key_words)
        exclusion_keywords_finder = DropRowsWithValuesInColumn(column='group', values=self.exclusion_key_words)
        group_cat_exclusion_keywords_finder = DropRowsWithValuesInColumn(column='group_cat',
                                                                         values=self.exclusion_key_words)

        new_tables: list[pd.DataFrame] = []
        for table_id, one_table in df.groupby('table_id', dropna=False):
            one_table = one_table.copy(deep=True)

            if one_table['group'].isna().all():
                new_tables.append(one_table)
                self.no_groups.append(table_id)
                continue

            inclusion_mask = inclusion_keywords_finder.find_mask(one_table)
            exclusion_mask = exclusion_keywords_finder.find_mask(one_table)
            group_cat_exclusion_mask = group_cat_exclusion_keywords_finder.find_mask(one_table)
            mask = inclusion_mask & ~exclusion_mask & ~group_cat_exclusion_mask

            histology_groups = one_table[mask].copy()
            if histology_groups['group'].unique().shape[0] == 0:

                if one_table['group'].isna().any():  # 25744580_page_2_table_0
                    # if one_table['group'].unique().shape[0] > 1 and one_table['group'].isna().any():  # 25744580_page_2_table_0
                    na_rows = one_table[one_table['group'].isna()]
                    new_tables.append(na_rows)
                    # print("Did not found proper group, but found NA rows in group column in", table_id)
                    continue

                # print(f"Did not found proper group. {table_id}. Groups: {one_table['group'].unique()}")
                self.tables_to_drop.append(table_id)
                continue

            if histology_groups['group'].unique().shape[0] > 1:
                multiple_finder = DropRowsWithValuesInColumn(column='group', values=self.inclusion_multiple_key_words)
                multiple_groups = pd.DataFrame({"group": histology_groups['group'].unique()})
                inclusion_mask = multiple_finder.find_mask(multiple_groups)
                if not inclusion_mask.any():
                    # print(f"Multiple groups, but no match: {table_id}: {histology_groups['group'].unique()}")
                    self.tables_to_drop.append(table_id)
                    continue

                chosen_groups = multiple_groups[inclusion_mask].group.tolist()
                # print(f"From {histology_groups['group'].unique()} following groups were chosen: {chosen_groups}")
                new_tables.append(
                    histology_groups[histology_groups['group'].isin(chosen_groups)].copy()
                )
                continue

            new_tables.append(histology_groups)

        print("Number of tables without correct groups: ", len(self.tables_to_drop))  # , "Tables:", self.tables_to_drop
        print("Number of tables without any groups:", len(self.no_groups))  # , "Tables:", self.no_groups)
        return pd.concat(new_tables)


class MergeCategoriesPerGroup(BaseModel, AbstractDFConverter):
    value_columns: list[str] = ['total_N', 'expr_n', 'expr_pct']
    category_columns: list[str] = None
    total_N_aggregate: Literal["sum", "mean", 'first'] = "mean"  # How to aggregate total_N
    expr_n_aggregate: Literal["sum", "mean"] = "sum"  # How to aggregate expr_n
    expr_pct_aggregate: Literal["sum", "mean"] = "sum"  # How to aggregate expr_pct
    differing_columns: list[str] = None

    def _merge_rows_within_group_cat(self, group_df: pd.DataFrame) -> pd.DataFrame | Union[int | None] | list[int]:
        group_df = group_df.copy(deep=True)

        # print(group_df['total_N'].unique())
        # if len(group_df[
        #            'total_N'].unique()) != 1:  # Total N is not the same for all rows, meaning that this is not the same g
        #     print(f"Unmapped expr_score found, investigate {group_df.iloc[0].PMID} {group_df.iloc[0].table_id}")
        #     raise ValueError()
        if len(group_df['total_N'].unique()) != 1:
            # self.tables_to_drop.append(group_df.iloc[0].table_id)
            print(f"Varying total_N, investigate {group_df.iloc[0].table_id}")
        first_index = group_df.index[0]
        indexes_to_drop = group_df.index[1:].tolist()

        aggregated = group_df.iloc[0][self.category_columns + ['PMID', 'table_id']].to_dict()
        _differing_columns = [col for col in self.differing_columns if col not in ('PMID', 'table_id')]
        print(self.total_N_aggregate)
        aggregated.update({
            'total_N': group_df['total_N'].iloc[0] if self.total_N_aggregate == "first" else (
                group_df['total_N'].mean() if self.total_N_aggregate == "mean" else group_df['total_N'].sum()),
            'expr_n': group_df['expr_n'].mean() if self.expr_n_aggregate == "mean" else group_df['expr_n'].sum(),
            'expr_pct': group_df['expr_pct'].mean() if self.expr_pct_aggregate == "mean" else group_df[
                'expr_pct'].sum(),
            **{
                merged_column: 'MRD: ' + ';'.join(group_df[merged_column].astype(str))
                for merged_column in _differing_columns
            },
        })
        # aggregated['expr_pct'] = aggregated['expr_n'] / aggregated['total_N'] * 100

        return pd.Series(aggregated), first_index, indexes_to_drop

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        self.differing_columns = list(set(df.columns).difference(set(self.value_columns)).difference(
            set(self.category_columns)))
        df = df.copy(deep=True)
        indexes_to_drop: list[int] = []
        for table_id in df.table_id.unique():
            one_table = df[df.table_id == table_id].copy()
            one_table = one_table.dropna(subset=self.value_columns, axis='rows')

            for group_key, group_df in one_table.groupby(self.category_columns, dropna=False):
                if len(group_df) == 1:
                    continue
                # print(group_df)
                aggregate, first_index, _indexes_to_drop = self._merge_rows_within_group_cat(group_df)
                df.loc[first_index] = aggregate
                indexes_to_drop.extend(_indexes_to_drop)
        print("Merged categories per group:", len(indexes_to_drop), "Set:", len(set(indexes_to_drop)))
        df = df.drop(indexes_to_drop)
        neg_duplicates_remover = RemoveNegativeDuplicates(
            category_columns=[col for col in self.category_columns if col != 'expr_type'],
            log=True
        )
        df = neg_duplicates_remover(df)
        return df
