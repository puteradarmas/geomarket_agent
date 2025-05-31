import re
import os
import json
from typing import Union
from hashlib import sha256

import requests

from jinja2 import Template
from pydantic import BaseModel
from pydantic_ai import Agent, ImageUrl, BinaryContent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from time import time

from schemas import ObservableFeatures


PATH_TO_PLACES = "data/top-10.json"
CACHE_DIR = "cache/img"
OUTPUT_DIR = "outputs/nearby"
GMAPS_API_KEY = "AIzaSyBMM3_s3QjI-5LNDDB5xwZoG28i_OBC3ek"
emuach_path = "E:/IMPORTANT_PICS/Reacts/emuach.jpg"

os.makedirs(OUTPUT_DIR, exist_ok=True)

VLM_PROMPT_TEMPLATE = Template("""\
Given a picture of a cafe, describe the image by looking for and paying attention to the following aspects:
- food or beverage items
- seating types
- the spacing between seats
- the decor / concept of the cafe
- lighting style
- is it indoor or outdoor?
- power outlets
- parking area
- restroom
- accessibility options
- prayer room
- charging stations
- bookshelves
- game area
\
""")

MOST_RELIABLE_VISUAL = {
    "food_and_beverage_options": ["coffee", "breakfast", "brunch", "lunch", "dinner", "dessert", "beer", "wine", "cocktails", "vegetarian"],
    "seating_types": ["counter", "tables", "couches", "communal", "booths"],
    "seating_spacing_level": ["cramped", "comfortable", "spacious"],
    "decor_style": ["industrial", "modern", "rustic", "eclectic", "minimalist"],
    "lighting_style": ["bright", "dim", "natural", "mixed"],
    "power_outlet_availability": ["none", "limited", "good", "abundant"],
    "has_outdoor_seating": ["true", "false"],
    "has_parking": ["true", "false"],
    "has_restroom": ["true", "false"],
    "has_accessibility_options": ["true", "false"],
    "has_prayer_room": ["true", "false"],
    "has_charging_stations": ["true", "false"],
    "has_bookshelf": ["true", "false"],
    "has_game_area": ["true", "false"],
}

llm = OpenAIModel(
    model_name="qwen2.5vl:3b",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)

agent: Agent[str] = Agent(model=llm, output_type=str)

with open(PATH_TO_PLACES, "r") as f:
    places = json.load(f)["places"]

place = places[0]
photos = place["photos"]
photos_path = [os.path.join(CACHE_DIR, sha256(p["name"].encode("utf-8")).hexdigest() + ".jpg") for p in photos]
photos_bin = []

for ppath in photos_path:
    assert os.path.exists(ppath)
    with open(ppath, "rb") as f:
        pbytes = f.read()
    photos_bin.append(BinaryContent(pbytes, "image/jpeg"))

for bcontent in photos_bin:
    print(f"------- inferencing for 1 images...")
    start = time()
    llm_input = [bcontent] + [VLM_PROMPT_TEMPLATE.render(parameters=MOST_RELIABLE_VISUAL)]
    result = agent.run_sync(llm_input)
    end = time()
    print(f"1 photos took {end-start} s")
    print(f"result: \n{result.output}")
    print("done inference --------------")