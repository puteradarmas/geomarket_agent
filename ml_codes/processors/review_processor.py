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

llm = OpenAIModel(
    model_name="qwen3-4b",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)
agent: Agent[str] = Agent(model=llm, output_type=str)

PROCESS_REVIEW_PROMPT = Template("""\
Given the following reviews of a cafe:

{{reviews}}

Perform an analysis by looking for evidence of and paying attention for the following aspects:
- staff_friendliness
- typical_wait_time
- service_style (described ordering/service process)
- noise_level (described acoustic environment)
- wifi_quality (does it exist? how reliable is it? poor/fair/good/excellent) 
- facilities (mentioned amenities: something like OUTDOOR_SEATING, BOOKSHELF, GAME_AREA, PRAYER_ROOM, CHARGING_STATIONS)
- power_outlet_availability
- work_friendly_features (mentions of laptop use/study suitability)

Use plain text without any markdown formatting in your analysis. It is okay to give your analysis a structure.
/nothink\
""")

def parse_format_reviews(reviews: list[dict]) -> list[str]:
    parsed_reviews = []
    for review in reviews:
        rating = review["rating"]
        text = review["text"]["text"]
        text = text.splitlines()
        text = [t for t in text if t != ""]
        text = " ".join(text)
        parsed_reviews.append(f"Rating: {rating}/5. Review: {text}")
    return parsed_reviews

def remove_think_tokens(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def process_reviews(reviews: list[dict]) -> str:
    parsed_reviews = parse_format_reviews(reviews)
    llm_result = agent.run_sync(PROCESS_REVIEW_PROMPT.render(reviews='\n'.join([f" - {p}" for p in parsed_reviews])))
    llm_output = llm_result.output
    llm_output = remove_think_tokens(llm_output)
    return llm_output
