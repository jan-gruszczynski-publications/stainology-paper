from glob import glob
from pathlib import Path

import pandas as pd


def get_papers(path: Path = Path("../data/res/papers/*.csv"), relevant: bool = False) -> pd.DataFrame:
    paths_to_papers = glob(str(path))
    dfs = [pd.read_csv(path) for path in paths_to_papers]
    papers = pd.concat(dfs)
    papers = papers.copy()
    papers.PMID = papers.PMID.astype(str).str.strip()
    papers = papers.drop_duplicates(subset=['PMID'])
    if relevant:
        papers = papers[papers.Relevant == "yes"]
    return papers

