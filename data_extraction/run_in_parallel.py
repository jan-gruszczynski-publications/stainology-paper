import concurrent
from pathlib import Path

from tqdm import tqdm

from data_extraction.data_loaders import get_papers
from data_extraction.table_data_extraction import process_table
from data_extraction.utils import load_json_from_file

if __name__ == '__main__':
    MODEL_NAME = "gemini/gemini-2.5-pro"
    MODEL_VERSION = "gemini_2_5_pro"

    PAPERS = get_papers("../res/new_papers2.csv")[["PMID", "Title", "Abstract"]]
    print("Papers shape:", PAPERS.shape)
    results_dir = Path("table_dir_results")
    results_dir.mkdir(exist_ok=True, parents=True)

    table_paths = load_json_from_file("table_paths.json")
    table_paths = [Path(x) for x in table_paths]
    # table_paths = table_paths[:160]
    print(table_paths)
    print(len(table_paths))

    MAX_WORKERS = 8
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_pmid = {}
        for _table_path in table_paths:
            try:
                paper_PMID = _table_path.stem.split("_")[0]
                paper = PAPERS[PAPERS["PMID"] == paper_PMID].iloc[0]
            except IndexError:
                print(f"Could not find paper with for {_table_path} in the CSV. Skipping.")
                continue

            future = executor.submit(
                process_table,
                _table_path,
                paper,
                results_dir
            )
            future_to_pmid[future] = _table_path

        for future in tqdm(concurrent.futures.as_completed(future_to_pmid), total=len(future_to_pmid)):
            pmid = future_to_pmid[future]
            try:
                future.result()
            except Exception as exc:
                print(f'PMID {pmid} generated an exception: {exc}')

    print("\n--- Parallel processing complete. ---")
