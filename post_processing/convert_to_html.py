from pathlib import Path

import markdown
import pandas as pd

from post_processing.consts import CSS
from post_processing.io_utils import get_image_file_as_base64_data
from post_processing.loaders import get_papers
from post_processing.loaders import path_with_old_content_root

RENAME_DICT = {
    'matched_tumour': 'MT',
    'expr_type': 'ET',
    'notes': 'NT',
    'stain': 'ST',
    'total_N': 'N',
    'tumour': 'T',
    'PMID': 'PMID',
    'expr_distribution': 'DST',
    'expr_pct': '%',
    'pattern': 'PT',
    'expr_n': 'n',
    'expr_score': 'SCR',
    'expr_intensity': 'INT',
    'expr_threshold': 'THR',
    'group': 'GRP',
    'group_cat': 'GC',
    'table_id': 'table_id'
}

REORDER_COLUMNS = [
    'ET', 'T', 'ST', 'N', 'n', '%', 'SCR', 'INT', 'THR', 'PT', 'DST', 'NT',
    'GRP', 'GC',
    'PMID', 'table_id'
]

PAPERS = get_papers("../concats/new_papers.csv")


def get_rename_and_reorder_dicts(df_columns: list[str],
                                 additional_rename: dict = None, additional_reorder: list = None) -> tuple[dict, list]:
    if not additional_rename:
        additional_rename = {}
    if not additional_reorder:
        additional_reorder = []
    if 'matched_tumour' in df_columns:
        rename_dict = {**RENAME_DICT, **additional_rename}
        reorder_columns = REORDER_COLUMNS.copy()
        reorder_columns.insert(2, 'MT')
        reorder_columns += additional_reorder
        # reorder_columns = ['M_T'] + REORDER_COLUMNS + additional_reorder
    else:
        rename_dict = {**RENAME_DICT, **additional_rename}
        del rename_dict['matched_tumour']
        reorder_columns = REORDER_COLUMNS + additional_reorder

    return rename_dict, reorder_columns


def convert_markdown_to_pdf(md_path: Path, base_path: Path):
    with open(md_path, "r", encoding="utf-8") as md_file:
        md_content = md_file.read()

    html_content = CSS + markdown.markdown(md_content, extensions=['extra', 'tables']) + "</div>"

    with open(base_path.joinpath(f"{md_path.stem}.html"), "w", encoding="utf-8") as html_file:
        html_file.write(html_content)


def write_abstracts_to_markdown(df: pd.DataFrame, df_backup: pd.DataFrame, path: Path,
                                additional_rename: dict = None, additional_reorder: list = None):  # 18246044
    rename_dict, reorder_columns = get_rename_and_reorder_dicts(df.columns.tolist(), additional_rename,
                                                                additional_reorder)
    df = df.copy().rename(columns=rename_dict)[reorder_columns]
    df_backup = df_backup.copy().rename(columns=rename_dict)[reorder_columns]

    df = df[~df.table_id.str.contains('table')]
    df_backup = df_backup[~df_backup.table_id.str.contains('table')]

    with open(path, 'w', encoding="utf-8") as md_file:
        md_file.write(f"# {path}\n")

    for PMID in df_backup.PMID.unique():
        one_paper = df[df.PMID == PMID].copy()
        one_paper = one_paper[one_paper.table_id.str.contains("abstract")]

        one_paper_backup = df_backup[df_backup.PMID == PMID].copy()
        one_paper_backup = one_paper_backup[one_paper_backup.table_id.str.contains("abstract")]

        paper_metadata = PAPERS[PAPERS.PMID == PMID].iloc[0]

        with open(path, 'a', encoding="utf-8") as md_file:
            md_file.write(f"### {paper_metadata.Title}\n")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{paper_metadata.PMID}"
            md_file.write(f"#### {paper_metadata.PMID} [{url}]({url})\n")
            md_file.write(f"\n{paper_metadata.Abstract}\n")
            md_file.write("\n")
            one_paper = one_paper.drop(columns=['PMID'])
            one_paper.to_markdown(buf=md_file, index=False, headers='keys', tablefmt='html')
            md_file.write("\n")
            md_file.write(f"Backup:")
            one_paper_backup = one_paper_backup.drop(columns=['PMID'])
            one_paper_backup.to_markdown(buf=md_file, index=False, headers='keys', tablefmt='html')
            md_file.write("\n\n---------------------------------------------\n")


def write_whole_papers_to_markdown(df: pd.DataFrame, df_backup: pd.DataFrame, path: Path,
                                   additional_rename: dict = None, additional_reorder: list = None):  # 18246044
    rename_dict, reorder_columns = get_rename_and_reorder_dicts(df.columns.tolist(), additional_rename,
                                                                additional_reorder)
    df = df.copy().rename(columns=rename_dict)[reorder_columns]
    df_backup = df_backup.copy().rename(columns=rename_dict)[reorder_columns]

    with open(path, 'w', encoding="utf-8") as md_file:
        md_file.write(f"# {path}\n")

    for PMID in df_backup.PMID.unique():
        # print(f"Processing PMID: {PMID}")
        one_paper = df[df.PMID == PMID].copy()
        # print(one_paper.table_id.unique())
        one_paper_abstract = one_paper[one_paper.table_id.str.contains("abstract")]

        one_paper_backup = df_backup[df_backup.PMID == PMID].copy()
        one_paper_backup_abstract = one_paper_backup[one_paper_backup.table_id.str.contains("abstract")]

        paper_metadata = PAPERS[PAPERS.PMID == PMID].iloc[0]
        with open(path, 'a', encoding="utf-8") as md_file:
            md_file.write(f"### {paper_metadata.Title}\n")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{paper_metadata.PMID}"
            md_file.write(f"#### {paper_metadata.PMID} [{url}]({url})\n")
            md_file.write(f"\n{paper_metadata.Abstract}\n")
            md_file.write("\n")

            md_file.write("Processed:")
            one_paper_abstract = one_paper_abstract.drop(columns=['PMID'])
            one_paper_abstract.to_markdown(buf=md_file, index=False, headers='keys', tablefmt='html')

            md_file.write(f"Original:")
            one_paper_backup_abstract = one_paper_backup_abstract.drop(columns=['PMID'])
            one_paper_backup_abstract.to_markdown(buf=md_file, index=False, headers='keys', tablefmt='html')
            # md_file.write("\n\n---------------------------------------------\n")
            # print(one_paper.table_id.unique())
            for table_id in one_paper_backup.table_id.unique():
                if "abstract" in table_id:
                    continue
                one_table = one_paper[one_paper.table_id == table_id].copy()
                one_table_backup = one_paper_backup[one_paper_backup.table_id == table_id].copy()

                md_file.write(f"\n##### Table ID: {table_id}\n")
                image_base64 = get_image_file_as_base64_data(
                    path_with_old_content_root(f"res\\pdf_table_images\\{table_id}.png"))
                md_file.write(f'<div class="image-container">')
                md_file.write(f'<img src="data:image/png;base64,{image_base64.decode("utf-8")}" class="table-image" />')
                md_file.write('</div>\n')

                md_file.write("Processed:")
                one_table = one_table.drop(columns=['PMID', 'table_id'])
                one_table.to_markdown(buf=md_file, index=False, headers='keys', tablefmt='html')
                md_file.write(f"Original:")
                one_table_backup = one_table_backup.drop(columns=['PMID', 'table_id'])
                one_table_backup.to_markdown(buf=md_file, index=False, headers='keys', tablefmt='html')

                md_file.write("\n\n---------------------------------------------\n")

            # one_paper = one_paper.drop(columns=['PMID'])
            # one_paper.to_markdown(buf=md_file, index=False, headers='keys', tablefmt='html')
            # md_file.write("\n")


def write_tables_to_markdown(df: pd.DataFrame, df_backup: pd.DataFrame, list_of_table_id: list[str], path: Path,
                             additional_rename: dict = None, additional_reorder: list = None):
    rename_dict, reorder_columns = get_rename_and_reorder_dicts(df.columns.tolist(), additional_rename,
                                                                additional_reorder)
    df = df.copy().rename(columns=rename_dict)[reorder_columns]
    df_backup = df_backup.copy().rename(columns=rename_dict)[reorder_columns]

    df = df[~df.table_id.str.contains('abstract')]
    df_backup = df_backup[~df_backup.table_id.str.contains('abstract')]

    with open(path, 'w', encoding="utf-8") as md_file:
        md_file.write(f"# {path}\n")

    for table_id in list_of_table_id:
        # one_paper = df[df.PMID == PMID].copy()
        one_table = df[df.table_id == table_id].copy()
        # if len(one_table) == 0:
        #     continue
        # print(one_table)

        # PMID = one_table.PMID.unique()[0]
        PMID = table_id.split('_')[0]  # Extract PMID from table_id

        # print(PMID)
        paper_metadata = PAPERS[PAPERS.PMID == PMID].iloc[0]

        with open(path, 'a', encoding="utf-8") as md_file:
            md_file.write(f"### {paper_metadata.Title}\n")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{paper_metadata.PMID}"
            md_file.write(f"#### {paper_metadata.PMID} [{url}]({url})\n")
            # md_file.write(f"\n{paper_metadata.Abstract}\n")
            md_file.write("\n")

            md_file.write(f"##### PMID: {PMID}, Table ID: {table_id}\n")
            image_base64 = get_image_file_as_base64_data(
                path_with_old_content_root(f"res\\pdf_table_images\\{table_id}.png"))
            md_file.write(f'<div class="image-container">')
            md_file.write(f'<img src="data:image/png;base64,{image_base64.decode("utf-8")}" class="table-image" />')
            md_file.write('</div>\n')

            one_table = one_table.drop(columns=['PMID', 'table_id'])
            one_table.to_markdown(buf=md_file, index=False, headers='keys', tablefmt='html')

            md_file.write("\n")
            md_file.write(f"Backup:")
            one_table_backup = df_backup[df_backup.table_id == table_id].copy()
            one_table_backup = one_table_backup.drop(columns=['PMID', 'table_id'])
            one_table_backup.to_markdown(buf=md_file, index=False, headers='keys', tablefmt='html')

            md_file.write("\n\n---------------------------------------------\n")

    # with open(path, "r", encoding="utf-8") as md_file:
    #     md_content = md_file.read()
    #
    # html_content = CSS + markdown.markdown(md_content, extensions=['extra', 'tables']) + "</div>"
    # with open(base_path.joinpath(f"{key}.html"), "w", encoding="utf-8") as html_file:
    #     html_file.write(html_content)

    # pdf_options = {
    #     'page-size': 'A4',
    #     'margin-top': '20mm',
    #     'margin-right': '20mm',
    #     'margin-bottom': '20mm',
    #     'margin-left': '20mm',
    #     'encoding': "UTF-8",
    #     'dpi': 300,
    #     'enable-local-file-access': None,
    #     'image-quality': 100,
    #     'enable-smart-shrinking': True
    # }
    #
    # pdfkit.from_string(html_content, base_path.joinpath(f"{key}.pdf"),
    #                    options=pdf_options,
    #                    configuration=pdfkit.configuration(
    #                        wkhtmltopdf="../data/wkhtmltopdf.exe"
    #                    ))
    # break
