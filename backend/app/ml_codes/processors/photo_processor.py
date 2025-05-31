from jinja2 import Template
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

vlm = OpenAIModel(
    model_name="qwen2.5vl:3b",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)
agent: Agent[None, str] = Agent(model=vlm, output_type=str)

VLM_PROMPT = """\
Given a picture of a cafe, describe the image by looking for and paying attention to the following aspects:
- food and beverages options (only the ones visible in the images)
- capacity_size (inferred from overall space and seating arrangements)
- seating_types (visible seating furniture)
- spacing_level (distance between tables/seats)
- decor_styles (visible interior design elements)
- lighting_style (light fixtures and natural light)
- facilities (visible amenities: something like OUTDOOR_SEATING, BOOKSHELF, GAME_AREA, PRAYER_ROOM, CHARGING_STATIONS, etc)
- power_outlet_availability (try to find power outlets in the picture. Is it scarce or abundant?)
- notable work friendly features.

Use unformatted paragraphs to describe each aspects.\
"""

def process_photo(
    imgbytes: list[bytes],
) -> str:
    imgbytes = [BinaryContent(imb, "image/jpeg") for imb in imgbytes]
    vlm_result = agent.run_sync(imgbytes + [VLM_PROMPT])
    vlm_output = vlm_result.output
    return vlm_output