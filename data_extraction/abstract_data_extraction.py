from pathlib import Path

import litellm
from langchain_core.prompts import PromptTemplate
from litellm.types.utils import ModelResponse

from data_extraction.abstracts_data_extraction_prompts import SYSTEM_ABSTRACT_PAIRS_PROMPT, USER_ABSTRACT_PAIRS_PROMPT
from data_extraction.utils import save_to_txt_file, save_json_to_file, extract_json_from_text


def extract_pairs(study_title: str, abstract: str, PMID: str, results_dir: Path) -> ModelResponse:
    user_prompt_template = PromptTemplate.from_template(USER_ABSTRACT_PAIRS_PROMPT)

    user_prompt = user_prompt_template.format_prompt(
        study_title=study_title,
        abstract=abstract
    ).to_string()

    save_to_txt_file(user_prompt, results_dir / f"{PMID}_user_prompt.txt")

    response = litellm.completion(
        model=MODEL_NAME,
        temperature=0.0,
        num_retries=2,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_ABSTRACT_PAIRS_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ]
    )
    return response


def process_abstract(study_title: str,
                     abstract: str,
                     pmid: str,
                     results_dir: Path,
                     load_cache: bool = True):
    path_to_full_response = results_dir / f"{pmid}_{MODEL_VERSION}_full_response.json"
    if path_to_full_response.exists() and load_cache:
        print(f"File {path_to_full_response} already exists, skipping.")
        return

    try:
        result = extract_pairs(study_title, abstract, pmid, results_dir)
    except Exception as e:
        print(f"Error processing {pmid}: {e}")
        return

    save_json_to_file(result.model_dump(), path_to_full_response)

    pairs_as_txt = result.choices[0].message.content
    save_to_txt_file(pairs_as_txt, results_dir / f"{pmid}_{MODEL_VERSION}_pairs.txt")
    print("Successfully processed:", pmid)

    try:
        pairs = extract_json_from_text(pairs_as_txt)
        save_json_to_file(pairs, results_dir / f"{pmid}_{MODEL_VERSION}_pairs.json")
    except Exception as e:
        return


if __name__ == "__main__":
    MODEL_NAME = "gemini/gemini-2.5-pro"
    MODEL_VERSION = "gemini_2_5_pro"

    pass
