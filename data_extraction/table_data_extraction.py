import os
from pathlib import Path

import litellm
import pandas as pd
from langchain_core.prompts import PromptTemplate
from litellm.types.utils import ModelResponse
from tqdm import tqdm

from data_extraction.data_loaders import get_papers
from data_extraction.table_extraction_prompts import SYSTEM_PAIRS_PROMPT, USER_PAIRS_PROMPT
from data_extraction.utils import encode_image, save_to_txt_file, save_json_to_file, extract_json_from_text

os.environ["GEMINI_API_KEY"] = ""
# os.environ["GEMINI_API_KEY"] = ""

def extract_pairs(path_to_image: Path, paper: pd.Series, results_dir: Path) -> ModelResponse:
    image_data = encode_image(path_to_image)
    image_media_type = 'image/png'

    user_prompt_template = PromptTemplate.from_template(USER_PAIRS_PROMPT)
    user_prompt = user_prompt_template.format_prompt(
        title=paper.Title,
        abstract=paper.Abstract
    )
    user_prompt = user_prompt.to_string().strip()
    save_to_txt_file(user_prompt, results_dir / f'{path_to_image.stem}_{MODEL_VERSION}_user_prompt.txt')

    response = litellm.completion(
        model=MODEL_NAME,  # Your existing model name
        temperature=0.0,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PAIRS_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{image_media_type};base64,{image_data}",
                            "format": image_media_type
                        }
                    }
                    ,
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ]
    )
    return response


def process_table(path_to_image: Path, paper: pd.Series, results_dir: Path):
    # if copy_image:
    #     try:
    #         shutil.copy(path_to_image, results_dir / path_to_image.name)
    #     except shutil.SameFileError:
    #         pass

    path_to_full_response = results_dir / f"{path_to_image.stem}_{MODEL_VERSION}_full_response.json"

    table_id = path_to_image.stem
    if path_to_full_response.exists():
        print(f"File already exists for : {table_id}")
        return

    try:
        result = extract_pairs(path_to_image, paper, results_dir)
    except Exception as e:
        print(f"Error processing {path_to_image.stem}: {e}")
        return


    save_json_to_file(result.model_dump(), path_to_full_response)

    pairs_as_txt = result.choices[0].message.content

    save_to_txt_file(pairs_as_txt, results_dir / f"{path_to_image.stem}_{MODEL_VERSION}.txt")
    print("Successfully processed:", path_to_image.stem)

    try:
        pairs = extract_json_from_text(pairs_as_txt)
        save_json_to_file(pairs, results_dir / f"{path_to_image.stem}_{MODEL_VERSION}.json")
    except Exception as e:
        return


if __name__ == '__main__':
    MODEL_NAME = "gemini/gemini-2.5-pro"
    MODEL_VERSION = "gemini_2_5_pro"

    PAPERS = get_papers("../res/new_papers2.csv")[["PMID", "Title", "Abstract"]]
    print("Papers shape", PAPERS.shape)

