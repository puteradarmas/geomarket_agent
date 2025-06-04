import json
import os
from processors.place_processor import process_place, process_opportunity

OUTPUT_DIR = "outputs/profiles"
PATH_TO_PLACES = "data/top-10.json"
PATH_TO_OPPORTUNITIES = "data/oppor-20.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(PATH_TO_PLACES, "r", encoding="utf8") as f:
    places = json.load(f)["places"]

for place in places:
    place_id = place["id"]
    print(f"Processing place {place_id}")
    fullpath = os.path.join(OUTPUT_DIR, f"{place_id}.json")
    if os.path.exists(fullpath):
        continue
    place_profile = process_place(place)
    if place_profile is None:
        print(f"Failed processing {place_id}")
        continue
    with open(fullpath, "w", encoding="utf8") as f:
        f.write(place_profile.model_dump_json(indent=2))
    
with open(PATH_TO_OPPORTUNITIES, "r", encoding="utf-8") as f:
    raw_opportunities = json.load(f)["places"]

