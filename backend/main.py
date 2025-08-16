import os
import json

from app.ml_codes.grab_locations import (
    grab_address,
    grab_locations_competitor,
    grab_locations_opportunity,
)
from app.ml_codes.processors.place_processor import (
    process_competitor_place,
    process_opportunity,
)
from app.ml_codes.recommendation import generate_recommendation
from app.ml_codes.schemas import CafeProfile, GeneralProfile, UserQuery

PROFILES_CACHE_PATH = "outputs/profiles/"
CACHE_PATH = "outputs/caches/"

os.makedirs(PROFILES_CACHE_PATH, exist_ok=True)
os.makedirs(CACHE_PATH, exist_ok=True)


def generate_recommendation_for_one_query(
    location: dict[str, float], request_id: str, additional_prompt: str
):
    competitors_cache = os.path.join(CACHE_PATH, f"{request_id}_competitors.json")
    opportunities_cache = os.path.join(CACHE_PATH, f"{request_id}_opportunities.json")

    if os.path.exists(competitors_cache):
        with open(competitors_cache) as f:
            json_locations_competitor = json.load(f)
    else:
        json_locations_competitor = grab_locations_competitor(
            location["lat"], location["lng"]
        )["places"]  # Get nearby cafes
        with open(competitors_cache, "w") as f:
            json.dump(json_locations_competitor, f, indent=2)

    if os.path.exists(opportunities_cache):
        with open(opportunities_cache) as f:
            json_locations_opportunities = json.load(f)
    else:
        json_locations_opportunities = grab_locations_opportunity(
            location["lat"], location["lng"]
        )["places"]  # Get nearby opportunities
        with open(opportunities_cache, "w") as f:
            json.dump(json_locations_opportunities, f, indent=2)

    # Process the opportunities
    processed_opportunities: list[GeneralProfile] = [
        process_opportunity(opp) for opp in json_locations_opportunities
    ]

    processed_competitors: list[CafeProfile] = []

    # Process the competitors
    for competitor in json_locations_competitor:
        place_id = competitor["id"]
        fullpath = os.path.join(
            PROFILES_CACHE_PATH, f"{place_id}.json"
        )  # Cache path for competitors profiles
        if os.path.exists(fullpath):
            with open(fullpath, "r", encoding="utf8") as f:
                cafe_profile = CafeProfile.model_validate_json(f.read())
        else:
            cafe_profile = process_competitor_place(competitor)
            with open(fullpath, "w", encoding="utf8") as f:
                f.write(cafe_profile.model_dump_json(indent=2))
        processed_competitors.append(cafe_profile)
    recommendation = generate_recommendation(  # Generate recommendation
        request_id=request_id,
        user_query=UserQuery(
            description=additional_prompt,
            latlong=[location["lat"], location["lng"]],
        ),
        opportunities_list=processed_opportunities,
        competitor_list=processed_competitors,
    )

    with open(f"recommendation_{request_id}.md", "w") as f:
        f.write(recommendation)


if __name__ == "__main__":
    additional_prompt = "the user wants to create a cafe that combines a multimedia studio (for filmmakers) and a cafe, so that the cafe can be a hangout spot for people in the scene. The main demographic is probably film students, hobbyists and professionals alike that are likely to need a dedicated studio for shooting and a good spot to hang out before or after."
    inputs = [
        # ("tebet_barat", (-6.239663628729565, 106.8480532100155)),
        # ("tebet_timur", (-6.228977500155005, 106.85375064227549)),
        ("dago_atas", (-6.870046395903662, 107.61963858654032)),
    ]
    for inp in inputs:
        req_id = inp[0]
        location = {
            "lat": inp[1][0],
            "lng": inp[1][1],
        }
        generate_recommendation_for_one_query(location, req_id, additional_prompt)
