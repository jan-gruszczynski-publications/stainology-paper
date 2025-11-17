import traceback
from pathlib import Path

import litellm
import pandas as pd
from langchain_core.prompts import PromptTemplate
from litellm.types.utils import ModelResponse
from tqdm import tqdm

from data_extraction.utils import encode_image, save_to_txt_file, save_json_to_file, extract_json_from_text
from data_extraction.who_classification_prompt import CLASSIFICATION_PROMPT_NO_JUSTIFICATION
from post_processing.group_utils import SelectHistologicalGroupFromTable


def WHO_mapping_to_str(WHO_mapping: pd.DataFrame) -> str:
    WHO_mapping['Category 1'] = WHO_mapping['Category 1'].fillna('[Unspecified Category 1]')
    WHO_mapping['Category 2'] = WHO_mapping['Category 2'].fillna('[Unspecified Category 2]')
    WHO_mapping['Definition'] = WHO_mapping['Definition'].fillna('[No definition provided]')

    output = []
    for category1 in WHO_mapping['Category 1'].unique():
        output.append(f"- Category 1: {category1}")
        sub_df = WHO_mapping[WHO_mapping['Category 1'] == category1]

        for category2 in sub_df['Category 2'].unique():
            output.append(f" -- Category 2: {category2}")
            sub_sub_df = sub_df[sub_df['Category 2'] == category2]

            for _, row in sub_sub_df.iterrows():
                output.append(f"  --- Category 3: {row['Tumour Class']}")
                output.append(f"      Definition: {row['Definition']}")
    final_output = '\n'.join(output)
    return final_output


def extract_tumour_names(__PMID:str, paper_info: pd.Series, tumour_names: list[dict],
                         who_categories_str: str,
                         paths_to_images: list[Path],
                         results_dir: Path) -> ModelResponse:
    image_media_type = 'image/png'
    encoded_images = []
    for path in paths_to_images:
        image_data = encode_image(path)
        encoded_images.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{image_media_type};base64,{image_data}",
                "format": image_media_type
            }
        })

    user_prompt_template = PromptTemplate.from_template(CLASSIFICATION_PROMPT_NO_JUSTIFICATION)
    user_prompt = user_prompt_template.format(
        tumour_names=str(tumour_names),
        title=paper_info["Title"],
        abstract=paper_info["Abstract"],
        publication_year=paper_info["EDAT"].strftime("%Y"),
        categories=who_categories_str,
    )
    save_to_txt_file(user_prompt, results_dir / f"{__PMID}_{MODEL_VERSION}_user_prompt.txt")

    response = litellm.completion(
        model=MODEL_NAME,
        # temperature=0.0,
        temperature=1.0,

        messages=[
            {
                "role": "user",
                "content": user_prompt.strip()
            }
        ]
    )
    return response


def process_PMID(_PMID: str,
                 paper_info: pd.Series,
                 concat_df: pd.DataFrame,
                 who_categories_str: str,
                 results_dir: Path):
    path_to_full_response = results_dir / f"{_PMID}_{MODEL_VERSION}_full_response.json"

    # if path_to_full_response.exists():
    #     print(f"File already exists for : {_PMID}")
    #     return

    one_paper_df = concat_df[concat_df.PMID == _PMID].copy(deep=True)
    if one_paper_df.empty:
        print(f"Warning: No data for PMID {_PMID} in concat_df. Skipping.")
        return

    one_paper_df = SelectHistologicalGroupFromTable()(one_paper_df)

    tumour_names_df = one_paper_df[['tumour', 'group', 'group_cat', 'notes', 'table_id']].copy()
    tumour_names_df = tumour_names_df.drop_duplicates(subset=['tumour', 'group', 'group_cat', 'notes']).reset_index(drop=True)
    table_ids = tumour_names_df['table_id'].unique().tolist()
    table_ids = [table_id for table_id in table_ids if "abstract" not in table_id]
    paths_to_images = [Path(f"../res/pdf_table_images/{table_id}.png") for table_id in table_ids]

    tumour_names_df = tumour_names_df.rename(columns={"group_cat": "group_category"})
    tumour_names_records = tumour_names_df.to_dict(orient='records')
    tumour_names = [
        {k: v for k, v in record.items() if pd.notna(v)}
        for record in tumour_names_records
    ]
    tumour_names = [
        {**record, 'idx': i + 1}
        for i, record in enumerate(tumour_names)
    ]
    # print(tumour_names)
    save_json_to_file(tumour_names, results_dir / f"{_PMID}_{MODEL_VERSION}_tumour_names.json")
    # # delete table_id from tumour names
    tumour_names = [{k: v for k, v in record.items() if k != 'table_id'} for record in tumour_names]

    if one_paper_df.empty:
        print(f"Warning: No data for PMID {_PMID} in concat_df. Skipping.")
        return

    try:
        result = extract_tumour_names(_PMID, paper_info, tumour_names, who_categories_str, paths_to_images, results_dir)
    except Exception as e:
        print(f"Error processing {_PMID}: {e}")
        traceback.print_exc()
        return

    save_json_to_file(result.model_dump(), path_to_full_response)

    pairs_as_txt = result.choices[0].message.content

    save_to_txt_file(pairs_as_txt, results_dir / f"{_PMID}_{MODEL_VERSION}_classification.txt")
    print("Successfully processed:", _PMID)

    try:
        pairs = extract_json_from_text(pairs_as_txt)
        save_json_to_file(pairs, results_dir / f"{_PMID}_{MODEL_VERSION}_classification.json")
    except Exception as e:
        return


if __name__ == '__main__':
    WHO_mapping = pd.read_excel("./Ovary Tumours from WHO Bluebook.xlsx",
                                index_col=0, skiprows=2).reset_index(drop=True)
    categories_str = WHO_mapping_to_str(WHO_mapping.copy())
    concat = pd.read_csv("./backup/***.csv", low_memory=False).astype({"PMID": str})

    MODEL_NAME = "gemini/gemini-2.5-pro"
    # MODEL_NAME = "gemini/gemini-2.5-flash"
    # MODEL_NAME = "gpt-5-mini"
    # MODEL_NAME = "gpt-5"
    # MODEL_VERSION = "gpt_5_mini"
    # MODEL_VERSION = "gemini_2_5_flash"
    MODEL_VERSION = "gemini_2_5_pro"
    # MODEL_VERSION = "gpt_5"
