import pandas as pd
from pydantic import BaseModel

from post_processing.pipeline_utils import AbstractDFConverter
from post_processing.remover_utils import remove_tables_from_df
from post_processing.string_cleaners import CleanColumn


class DropIfNNAInRow(BaseModel, AbstractDFConverter):
    columns: list[str] = ['expr_n', 'expr_pct', 'total_N']
    n: int = 2

    def __call__(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df = df.copy(deep=True)
        mask = df[self.columns].isna().sum(axis=1) >= self.n
        print(f"Dropped rows with {self.n} or more NAs in columns {self.columns}: {mask.sum()}")
        return df[~mask]


class DropTableIDsWithValuesInColumn(BaseModel, AbstractDFConverter):
    column: str
    values: list[str]

    def __call__(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df = df.copy(deep=True)
        filtered = df[df[self.column].isin(self.values)]
        return df[~df.table_id.isin(filtered.table_id.unique())]


class DropRowsWithValuesInColumn(BaseModel):
    column: str = 'matched_tumour'
    values: list[str] = ['Not matched', 'Artificial taxon', 'Not Ovarian']

    def find_mask(self, df: pd.DataFrame) -> pd.Series:
        if not self.values:
            return pd.Series([False] * len(df), index=df.index)

        col_series = CleanColumn()(df[self.column])
        pattern = '|'.join([val.lower().strip() for val in self.values])
        mask = col_series.str.lower().str.contains(pattern, na=False)
        return mask

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        mask = self.find_mask(df)
        print(f"Rows dropped with values {self.values} in column: {self.column}", mask.sum())
        return df[~mask]


class DropRowsWithValuesInColumnExactMatch(BaseModel):
    column: str
    values: list[str]
    debug_info: bool = True

    def find_mask(self, df: pd.DataFrame) -> pd.Series:
        col_series = CleanColumn()(df[self.column])
        mask = col_series.isin([val.lower().strip() for val in self.values])
        if self.debug_info:
            for val in self.values:
                count = (col_series == val.lower().strip()).sum()
                print(f"Value '{val}' matched {count} rows.")
        return mask

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        mask = self.find_mask(df)
        print(f"Rows dropped with values {self.values}", mask.sum())
        return df[~mask]


class FilterTablesWithValuesInColumn(BaseModel, AbstractDFConverter):
    column: str
    values: list[str]

    def __call__(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df = df.copy(deep=True)

        df.stain = df.stain.str.replace("-", "")
        df.stain = df.stain.str.replace(" ", "")
        self.values = list(map(lambda x: x.replace("-", "").replace(" ", ""), self.values))

        finder = DropRowsWithValuesInColumn(column=self.column, values=self.values)
        have_keywords_mask = finder.find_mask(df)
        rows_with_keywords = df[have_keywords_mask]
        # rows_with_keywords = df[df[self.column].isin(self.values)]
        table_ids_with_no_keywords = list(set(df.table_id.unique().tolist())
                                          .difference(set(rows_with_keywords.table_id.unique().tolist())))
        # print(table_ids_with_no_keywords)
        return remove_tables_from_df(df, table_ids_with_no_keywords)


# class DropRowsWithValuesInColumn(BaseModel, AbstractDFConverter):
#     column: str = 'matched_tumour'
#     with_values: list[str] = ['Not matched', 'Artificial taxon', 'Not Ovarian']
#
#     def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
#         lower_and_stripped = CleanColumn()(df[self.column])
#         # may contain string
#         not_ovarian = lower_and_stripped.isin([val.lower().strip() for val in self.with_values])
#         # not_ovarian = df[self.column_name].isin(self.with_values)
#         print("Not Ovarian:", sum(not_ovarian.astype(int)))
#         return df[~not_ovarian]


class DropNARowsInColumns(BaseModel, AbstractDFConverter):
    columns: list[str] = ['matched_tumour', 'stain']

    def __call__(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df = df.copy()
        for col in self.columns:
            na_rows = df[pd.isna(df[col])]
            print(f"NA in {col}:", len(na_rows))
            # self.singleton.my_dict[f'no_{col}'] = na_rows
            df = df.dropna(subset=[col]).copy()
        return df
        # missing_stain = df[df.stain_name.isin(['unknown'])]
        # print("Missing stain:", len(missing_stain))
        # # self.singleton.my_dict['missing_stain'] = missing_stain
        # return df[~df.stain_name.isin(['unknown'])]


class DropAllRowsThatHaveNotNumericSigns(BaseModel, AbstractDFConverter):
    column: str = 'expr_pct'

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy(deep=True)

        def is_numeric_or_nan(x):
            if isinstance(x, (int, float)):
                return True
            if pd.isna(x):
                return True
            if isinstance(x, str):
                try:
                    float(x)
                    return True
                except ValueError:
                    return False
            return False

        mask = df[self.column].apply(is_numeric_or_nan)
        print("Removed rows with non-numeric signs in column", self.column, ":", df.shape[0] - df[mask].shape[0])
        return df[mask]

# Old version removed after peer review.
# class DropAllRowsThatHaveNotNumericSigns(BaseModel, AbstractDFConverter):
#     column: str = 'expr_pct'
#
#     def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
#         df = df.copy(deep=True)
#         mask = df[self.column].apply(lambda x: isinstance(x, (int, float)) or pd.isna(x))
#         print("Removed rows with non-numeric signs in column", self.column, ":", df.shape[0] - df[mask].shape[0])
#         return df[mask]


class TakeIfAllInColumnsNA(BaseModel, AbstractDFConverter):
    columns: list[str] = ['expr_score', 'expr_intensity', 'expr_threshold', 'expr_distribution', 'notes']

    def __call__(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df = df.copy(deep=True)
        mask = df[self.columns].isna().all(axis=1)
        print("Rows with not NaN in columns", self.columns, ":", df.shape[0] - mask.sum())
        return df[mask]


class FilterExcludedPaper(BaseModel, AbstractDFConverter):
    """
    Filter papers that are excluded from the analysis.
    """
    excluded_papers_PMIDs: list[str] = []

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy(deep=True)
        if not self.excluded_papers_PMIDs:
            return df
        mask = ~df.PMID.isin(self.excluded_papers_PMIDs)
        print(f"Filtered out {df.shape[0] - df[mask].shape[0]} excluded rows from {df.shape[0]}.")
        return df[mask]