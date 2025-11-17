from pathlib import Path

import numpy as np
import pandas as pd
from pydantic import BaseModel

from post_processing.io_utils import load_json_from_file
from post_processing.pipeline_utils import AbstractDFConverter, Pipeline
from post_processing.string_cleaners import CleanColumn


def _load_tumour_mappings(dir_path: Path, glob_query: str = "*2_5_pro_tumour_mapping.json") -> dict[str, list[dict]]:
    tumour_mappings = {}
    for file in dir_path.glob(glob_query):
        PMID = file.stem.split("_")[0]
        tumour_mappings[PMID] = load_json_from_file(file)
    return tumour_mappings


def load_tumour_mappings_as_df(results_dir: Path = Path("../../data_retrieval/batch_results/"),
                               model_glob_key: str = "*_gemini*"):
    tumour_names = _load_tumour_mappings(results_dir,
                                         glob_query=f"{model_glob_key}_tumour_names.json")

    tumour_mappings = _load_tumour_mappings(results_dir,
                                            glob_query=f"{model_glob_key}_classification.json")


    def _transform_to_df(mapping: dict[str, list[dict]]) -> pd.DataFrame:
        rows = []
        for pmid, list_of_dict in mapping.items():
            for a_dict in list_of_dict:
                a_dict['PMID'] = pmid
                rows.append(a_dict)
        return pd.DataFrame(rows)

    tumour_names = _transform_to_df(tumour_names)
    tumour_mappings = _transform_to_df(tumour_mappings)
    print("Tumour names shape:", tumour_names.shape, "Tumour mappings shape:", tumour_mappings.shape)
    print("Unique PMIDs in tumour names:", tumour_names['PMID'].nunique(),
          "Unique PMIDs in tumour mappings:", tumour_mappings['PMID'].nunique())
    if 'justification' in list(tumour_mappings.columns):
        tumour_mappings = tumour_mappings[['idx', 'tumour', 'who_mapping', 'PMID', 'justification']]
    else:
        tumour_mappings = tumour_mappings[['idx', 'tumour', 'who_mapping', 'PMID']]
    tumour_mappings = tumour_mappings.merge(tumour_names, how='right', on=['idx', 'tumour', 'PMID'])
    return tumour_mappings.rename(columns={'who_mapping': 'matched_tumour', 'group_category': 'group_cat'}).drop(columns=['idx'])


class TumourMapperV3(BaseModel, AbstractDFConverter):
    path_to_tumour_mappings: Path = Path("../../data_retrieval/batch_results/")
    model_glob_key: str = "*_gemini_*"
    on: list[str] = ['PMID', 'tumour', 'group', 'group_cat', 'notes']
    apply_cleaning: bool = True

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        tumour_mappings = load_tumour_mappings_as_df(self.path_to_tumour_mappings, self.model_glob_key)
        print("Pre tumour-mapping shape:", df.shape)

        if self.apply_cleaning:
            tumour_mappings.loc[
                tumour_mappings['matched_tumour'] == 'Artificial Taxon', 'matched_tumour'] = 'Artificial taxon'
            tumour_mappings.loc[tumour_mappings['matched_tumour'] == 'Metastasis to ovary', 'matched_tumour'] \
                = 'Metastases to the Ovary'
            column_processing_map = {col: CleanColumn() for col in self.on}
            cleaning_piepline = Pipeline(column_processing_map, [])
            tumour_mappings = cleaning_piepline(tumour_mappings)

        if tumour_mappings.empty:
            raise ValueError("Tumour mappings df is empty, check the path or glob key.")

        duplicates_mask = tumour_mappings.duplicated(subset=self.on, keep=False)
        print("Number of duplicates in tumour mappings:", duplicates_mask.sum())
        tumour_mappings = tumour_mappings.drop_duplicates(subset=self.on)


        mapped_df = df.merge(tumour_mappings, on=self.on, how='left')

        overlapping = [col[:-2] for col in mapped_df.columns if
                       col.endswith('_x') and f"{col[:-2]}_y" in mapped_df.columns]
        for col in overlapping:
            mapped_df[col] = mapped_df[f"{col}_x"]
            mapped_df.drop([f"{col}_x", f"{col}_y"], axis=1, inplace=True)
        print("Post tumour-mapping shape:", mapped_df.shape)
        print("Unmapped:", mapped_df[mapped_df.matched_tumour.isna()].shape)
        return mapped_df


class TumourMapperV2(BaseModel, AbstractDFConverter):
    tumour_mappings: dict[str, dict] = None
    path_to_tumour_mappings: Path = Path("../data_retrieval/tumours_classification_2_5_pro/")
    new_column_name: str = 'matched_tumour'
    mapped_column_name: str = 'tumour'
    skip_not_mapped: bool = False
    missing: list[str] = []

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        self.tumour_mappings = _load_tumour_mappings(self.path_to_tumour_mappings)
        if not self.tumour_mappings:
            raise ValueError(f"No tumour mappings found in {self.path_to_tumour_mappings}. "
                             f"Please ensure the directory contains JSON files with tumour mappings.")
        df = df.copy(deep=True)
        self.missing = []
        list_of_mapped_group_dfs = []
        for PMID, group_df in df.groupby('PMID', dropna=False):
            group_df = group_df.copy(deep=True)
            try:
                tumour_mapping = self.tumour_mappings[PMID]
            except KeyError:
                if not self.skip_not_mapped:
                    list_of_mapped_group_dfs.append(group_df)
                continue

            def map_tumour_name(tumour_name: str) -> str | float:
                if pd.isna(tumour_name):
                    return tumour_name
                try:
                    return tumour_mapping[tumour_name]
                except KeyError:
                    tumour_mapping_lower_keys = {k.lower(): v for k, v in tumour_mapping.items()}
                    tumour_name_lower = tumour_name.lower()
                    try:
                        return tumour_mapping_lower_keys[tumour_name_lower]
                    except KeyError:
                        self.missing.append(tumour_name)
                        return np.nan

                        # print(PMID)
                        # print(tumour_name)
                        # print(tumour_mapping)
                        # raise

            group_df.insert(4, self.new_column_name, group_df[self.mapped_column_name].apply(map_tumour_name))
            list_of_mapped_group_dfs.append(group_df)

        return pd.concat(list_of_mapped_group_dfs)


class TumourMapperV1:

    def __init__(self, clean_pipeline: callable,
                 mapped_column_name: str = 'tumour',
                 new_column_name: str = 'matched_tumour'):
        dictionary = pd.read_excel('../data/res/tumour_name_dictionary.xlsx')
        dictionary.tumour_unmatched = clean_pipeline(dictionary.tumour_unmatched)
        dictionary = dictionary.dropna(subset=['tumour_class'])
        dictionary['tumour_unmatched'] = dictionary['tumour_unmatched'].str.replace('tumors', 'tumour')
        dictionary['tumour_unmatched'] = dictionary['tumour_unmatched'].str.replace('tumours', 'tumour')
        dictionary['tumour_unmatched'] = dictionary['tumour_unmatched'].str.replace('tumor', 'tumour')
        dictionary['tumour_unmatched'] = dictionary['tumour_unmatched'].str.replace('-', ' ')

        self.mapping = dictionary.set_index('tumour_unmatched')['tumour_class'].to_dict()

        self.mapped_column_name: str = mapped_column_name
        self.new_column_name: str = new_column_name

    def replace_tumour_name(self, tumour_name: str) -> str:
        tumour_name = tumour_name.lower().strip()
        tumour_name = tumour_name.replace('tumors', 'tumour')
        tumour_name = tumour_name.replace('tumours', 'tumour')
        tumour_name = tumour_name.replace('tumor', 'tumour')
        tumour_name = tumour_name.replace('-', ' ')
        try:
            return self.mapping[tumour_name]
        except KeyError:
            return "Not matched"

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.insert(0, self.new_column_name, df[self.mapped_column_name].apply(self.replace_tumour_name))
        return df
