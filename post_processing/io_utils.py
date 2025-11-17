import base64
import json
from pathlib import Path


def get_model_version(model_name: str) -> str:
    if model_name == "gemini/gemini-2.5-pro" or model_name == "gemini-2.5-pro":
        return "gemini_2_5_pro"
    if model_name == "openai/gpt-4o-mini":
        return "gpt_4o_mini"
    if model_name == "openai/chatgpt-4o-latest":
        return "chatgpt_4o_latest"
    if model_name == "gemini/gemini-2.5-flash" or model_name == "gemini-2.5-flash":
        return "gemini_2_5_flash"
    parts = model_name.split("-")
    model_name = f"{parts[3]}_{parts[1]}_{parts[2]}"
    model_name = model_name.replace(".", "_")
    return model_name


def get_image_file_as_base64_data(file_path: str) -> bytes:
    with open(file_path, 'rb') as image_file:
        return base64.b64encode(image_file.read())


def encode_image(image_path) -> str:
    # Read the image file in binary mode
    with open(image_path, 'rb') as image_file:
        # Read the binary data
        image_bytes = image_file.read()

    # Encode the image bytes to base64 string
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')

    return encoded_image


# function that takes a string and saves to txt file
def save_to_txt_file(text: str, file_path: str | Path):
    with open(file_path, 'w+', encoding="utf-8") as file:
        file.write(text)


# function that loads text from a txt file
def load_from_txt_file(file_path: str | Path) -> str:
    with open(file_path, 'r', encoding="utf-8") as file:
        return file.read()


# save json
def save_json_to_file(data: dict, file_path: str | Path):
    with open(file_path, 'w+', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)


# load json
def load_json_from_file(file_path: str | Path) -> dict:
    with open(file_path, 'r') as json_file:
        return json.load(json_file)
