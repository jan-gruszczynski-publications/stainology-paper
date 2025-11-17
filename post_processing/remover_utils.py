import pandas as pd


def remove_all_pairs_with_the_same_stain_and_tumour_by_table_id(df: pd.DataFrame, indexes: list[int]) -> pd.DataFrame:
    df = df.copy(deep=True)
    to_delete = df.loc[indexes]
    to_delete = to_delete[['tumour', 'stain', 'table_id']].drop_duplicates()

    df_merged = df.merge(
        to_delete,
        on=['tumour', 'stain', 'table_id'],
        how='left',
        indicator=True
    )
    print("Removed rows with the same tumour and stain:", len(df_merged[df_merged['_merge'] == 'both']))
    return df_merged[df_merged['_merge'] == 'left_only'].drop(columns=['_merge'])


def remove_tables_from_df(df: pd.DataFrame, table_ids: list[str]) -> pd.DataFrame:
    df = df.copy(deep=True)
    df = df[~df.table_id.isin(table_ids)]
    print("Removed tables:", len(table_ids))
    return df
