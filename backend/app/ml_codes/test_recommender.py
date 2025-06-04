import json
from glob import glob
import os

from recommendation import generate_recommendation
from processors.place_processor import process_opportunity
from grab_locations import grab_distance

from schemas import CafeProfile, UserQuery, GeneralProfile

PATH_TO_OPPORTUNITIES = "data/oppor-20.json"
PATHS_TO_PARSED_CAFE_PROFILES = glob("outputs/profiles/C*.json")
OPPORTUNITY_CACHE = "outputs/opportunities/opportunities.json"
RECOMMENDATIONS_CACHE = "outputs/recommendations"
os.makedirs(os.path.dirname(OPPORTUNITY_CACHE), exist_ok=True)
os.makedirs(os.path.dirname(RECOMMENDATIONS_CACHE), exist_ok=True)

if not os.path.exists(OPPORTUNITY_CACHE):
    with open(PATH_TO_OPPORTUNITIES, "r", encoding="utf-8") as f:
        raw_opportunities = json.load(f)["places"]
    opportunities: list[GeneralProfile] = []
    for oppor in raw_opportunities:
        opportunity = process_opportunity(oppor)
        opportunity.distance_to_point = grab_distance(
            -6.174904869095269, 
            106.8271353670165,
            opportunity.latlong[0],
            opportunity.latlong[1]
        )
        opportunities.append(opportunity)
    with open(OPPORTUNITY_CACHE, "w", encoding="utf-8") as f:
        json.dump([
            oppy.model_dump(mode="json") for oppy in opportunities
        ], f)
else:
    with open(OPPORTUNITY_CACHE, "r", encoding="utf-8") as f:
        raw_opportunities = json.load(f)
    opportunities = [
        GeneralProfile.model_validate_json(json.dumps(oppy)) for oppy in raw_opportunities
    ]


competitors = []

user_cafe_id = "MONAS"

for cafe_profile_path in PATHS_TO_PARSED_CAFE_PROFILES:
    with open(cafe_profile_path, "r", encoding="utf8") as f:
        cafe_profile = CafeProfile.model_validate_json(f.read())
    competitors.append(cafe_profile)

recommendation = generate_recommendation(
    user_cafe_id,
    UserQuery(
        description="A book cafe with ample selections of coffee, pastries and light bites. Every seats equipped with an electrical outlet and wifi is provided with a nice music ambiance. Ideal for working and hanging out while reading our selection of books.",
        latlong=[-6.174904869095269, 106.8271353670165]
    ),
    opportunities,
    competitors
)

print(recommendation)
with open(os.path.join(RECOMMENDATIONS_CACHE, f"{user_cafe_id}.md"), "w", encoding="utf8") as f:
    f.write(recommendation)