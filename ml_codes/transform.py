import json
import os
import re
from hashlib import sha256
from io import BytesIO
from typing import Union

import requests
from jinja2 import Template
from PIL import Image
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from schemas import ObservableFeatures

PATH_TO_PLACES = "data/top-10.json"
OUTPUT_DIR = "outputs/nearby"
CACHE_DIR = "cache/img"
GMAPS_API_KEY = "AIzaSyBMM3_s3QjI-5LNDDB5xwZoG28i_OBC3ek"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

vlm = OpenAIModel(
    model_name="qwen2.5vl:3b",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)

llm = OpenAIModel(
    model_name="qwen3-4b",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)

agent: Agent[None, str] = Agent(model=vlm, output_type=str)
reformat_agent: Agent[None, Union[ObservableFeatures, str]] = Agent(model=llm, output_type=[ObservableFeatures, str])

VLM_PROMPT_TEMPLATE = Template("""\
Role:
Position yourself as a professional cafe / coffeshop reviewer. You are adept at profiling a cafe.
---
Instruction:
You are given this schema, detailing the attributes / profiles of a cafe along with their possible values.

{{schema}}

You are given a set of pictures taken in a cafe / coffeeshop. 
Rigorously examine for evidence in the pictures to fill the profile and attributes detailed above.

Example analysis:
- ... I can also see a picture being situated in what looks like an outdoor space. It has tables and seating, so it means the cafe has outdoor seating. I should set `outdoor_seating` to true.
- ... One picture shows a couch-like seating, while another shows a typical counter seating you can find in cafes. Since i dont see any other types of seating, `seating_types` should include ["counter", "couches"]
- ... A picture shows a table with a toast and coffee being served. This means the cafe offers breakfast options and coffee, and have a table seating. I should set `serves` to ["coffee", "breakfast"] and `seating_types` should include ["tables"]

When direct evidence / proof isn't available, do not make assumptions.
After the analysis, provide the output using the above schema.
---
Output:

Analysis: your analysis here
Profile: Use the above schema\
""")

JSON_REFORMAT_TEMPLATE = Template("""\
Reformat this following input

{{llm_output}}

To follow this schema:

{{schema}}
""")


def grab_photo_from_gmaps(photo_url, api_key, maxsize=800):
    img_name = sha256(photo_url.encode("utf-8")).hexdigest() + ".jpg"
    fullpath = os.path.join(CACHE_DIR, img_name)
    if os.path.exists(fullpath):
        with open(fullpath, "rb") as f:
            imgbytes = f.read()
        return "image/jpeg", imgbytes
    full_url = "https://places.googleapis.com/v1/" + photo_url + "/media"
    response = requests.get(
        full_url,
        params={
            "key": api_key,
            "maxHeightPx": maxsize,
            "maxWidthPx": maxsize,
            "skipHttpRedirect": True,
        },
    )
    print(response.json())
    if response.status_code != 200:
        return None
    uri = response.json()["photoUri"]
    response.close()
    response = requests.get(uri, stream=True)
    if response.status_code != 200:
        return None
    chunks = bytearray()
    for chunk in response.iter_content(1024):
        chunks.extend(chunk)

    image = Image.open(BytesIO(chunks))
    image.save(fullpath)

    return "image/jpeg", bytes(chunks)

def remove_think_tokens(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

@reformat_agent.tool_plain
def parse_schema(input_schema: ObservableFeatures) -> ObservableFeatures:
    return input_schema

def analyze_cafe_profile_from_image(
    img_bytes, img_type, keywords, max_reconnect_attempt=3, max_reformat_attempt=3
):
    last_exception = None
    llm_call_result = None
    for attempt in range(max_reconnect_attempt):
        try:
            result = agent.run_sync(
                [
                    VLM_PROMPT_TEMPLATE.render(schema=ObservableFeatures.model_json_schema()),
                    BinaryContent(img_bytes, media_type=img_type),
                ]
            )
            llm_call_result = result
            break
        except Exception as ex:
            last_exception = ex
    if llm_call_result is None:
        return None
    latest_llm_output = result.output
    print(latest_llm_output)
    final_output = None
    reformat_needed = False
    for attempt in range(max_reformat_attempt + 1):
        try:
            if reformat_needed:
                reformat_output = reformat_agent.run_sync(
                    JSON_REFORMAT_TEMPLATE.render(llm_output=latest_llm_output)
                )
                latest_llm_output = reformat_output.output
            cleaned_llm_output = remove_think_tokens(latest_llm_output)
            final_output = json.loads(cleaned_llm_output)
            break
        except Exception as ex:
            reformat_needed = True
            last_exception = ex
    if final_output is None:
        raise ValueError(f"Failed VLM inference for img: {last_exception}")
    return final_output


with open(PATH_TO_PLACES, "r", encoding="utf-8") as f:
    places = json.load(f)["places"]

for place in places:
    place_output_dir = os.path.join(OUTPUT_DIR, f"{place['id']}")
    os.makedirs(place_output_dir, exist_ok=True)
    photos = place["photos"]
    for photo in photos:
        img_type, imgbytes = grab_photo_from_gmaps(photo["name"], GMAPS_API_KEY)
        keywords = extract_keywords_from_image(imgbytes, img_type, parameters)
        # print(keywords)
        # exit()
