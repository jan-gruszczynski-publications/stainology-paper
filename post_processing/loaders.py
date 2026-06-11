from glob import glob
from pathlib import Path
from typing import Literal

import pandas as pd

from post_processing.io_utils import load_json_from_file

CONTENT_ROOT = "C:\\Users\\***\\Desktop\\Projects\\stainology\\"
OLD_CONTENT_ROOT = "C:\\Users\\***\\Desktop\\Projects\\***"


def path_with_content_root(path: str | Path) -> Path:
    assert str(path)[0] != "/", "Provide path without leading slash"

    if isinstance(path, str):
        path = Path(path)
    return Path(CONTENT_ROOT) / path


def path_with_old_content_root(path: str | Path) -> Path:
    assert str(path)[0] != "/", "Provide path without leading slash"

    if isinstance(path, str):
        path = Path(path)
    return Path(OLD_CONTENT_ROOT) / path


def load_stains(file_path: str) -> list[str]:
    with open(file_path, 'r') as file:
        stains = file.read().splitlines()
    return [stain.strip() for stain in stains if stain.strip()]


def get_pairs(dir_path: Path, glob_query: str = "*_pairs.json",
              mode: Literal["abstract", "table"] = 'abstract') -> pd.DataFrame:
    files = list(dir_path.glob(glob_query))

    pairs_dfs = []
    for file in files:
        pairs_as_json = load_json_from_file(file)
        pairs_as_df = pd.DataFrame(pairs_as_json)
        pairs_as_df = pairs_as_df.rename(columns={'intensity': 'expr_intensity',
                                                  'exp_intensity': 'expr_intensity',
                                                  'score': 'expr_score',
                                                  'exp_score': 'expr_score',
                                                  'expression_intensity': 'expr_intensity',
                                                  'expr_intensity': 'expr_intensity',
                                                  'threshold': 'expr_threshold',
                                                  'exp_threshold': 'expr_threshold',
                                                  'distribution': 'expr_distribution',
                                                  'expr_pattern': 'pattern'
                                                  })
        try:
            pairs_as_df = pairs_as_df.drop(columns=['group_cat_2', 'group_2'])
        except KeyError:
            pass
        # if 'intensity' in pairs_as_df.columns:
        #     pairs_as_df = pairs_as_df.rename(columns={'intensity': 'exp_intensity'})
        # if 'score' in pairs_as_df.columns:
        #     pairs_as_df = pairs_as_df.rename(columns={'score': 'exp_score'})
        PMID = file.name.split("_")[0]
        pairs_as_df['PMID'] = PMID
        match mode:
            case "abstract":
                # pairs_as_df['is_abstract'] = True
                pairs_as_df['table_id'] = f"{PMID}_abstract"
            case "table":
                # pairs_as_df['is_abstract'] = False
                pairs_as_df['table_id'] = file.name.split("_gemini_")[0]

            case _:
                raise ValueError(f"Invalid mode: {mode}. Use 'abstract' or 'table'.")

        pairs_dfs.append(pairs_as_df)

    df = pd.concat(pairs_dfs)
    return df.reset_index(drop=True)


def get_papers(path: Path | str = Path("../data/res/papers/*.csv"), relevant: bool = False) -> pd.DataFrame:
    paths_to_papers = glob(str(path))
    dfs = [pd.read_csv(path) for path in paths_to_papers]
    papers = pd.concat(dfs)
    papers = papers.copy()
    papers.PMID = papers.PMID.astype(str).str.strip()
    papers = papers.drop_duplicates(subset=['PMID'])
    if relevant:
        papers = papers[papers.Relevant == "yes"]

    papers.EDAT = pd.to_datetime(papers.EDAT)

    return papers.drop(columns=["Unnamed: 0"])
