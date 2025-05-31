import json
import os
import re
from hashlib import sha256
from io import BytesIO

import requests
from jinja2 import Template
from PIL import Image
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from processors.photo_processor import process_photo
from processors.review_processor import process_reviews, remove_think_tokens
from schemas import CafeProfile, GeneralProfile

llm = OpenAIModel(
    model_name="qwen3-4b",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)
agent: Agent[str] = Agent(model=llm, output_type=str)
reformat_agent: Agent[CafeProfile] = Agent(model=llm, output_type=CafeProfile, output_retries=3)


OUTPUT_DIR = "outputs/intermediate"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CACHE_DIR = "cache/img"
GMAPS_API_KEY = "AIzaSyBMM3_s3QjI-5LNDDB5xwZoG28i_OBC3ek"


CONSOLIDATE_SUMMARIES_PROMPT = Template("""\
Background:
You are trying to profile a cafe location based on its reviews and some pictures taken inside of it.
A separate process has been done to summarize the reviews and the pictures.
----
Instruction:
Given a summary of the reviews, and a set of summaries from photos, consolidate all of them into a unified representation following the provided schema.
Each values in the schema may have a set of enumerated values. Where applicable, first map the values you found into these values.
To structure your thoughts, first list all of the parameters observed in the pictures or reviews. Then list all the values observed for each parameter, merging values found from reviews or photo summaries.
Afterwards, for enumerated values, map these values into one of the possible values. Leave non-enum values as-is.
Do not assume values. Use only all the information given to you.
Then generate the schema using the information you have listed, merged and mapped.

Review summary:

{{review_summary}}

Photo summaries:

{{photo_summaries}}
----
Schema:

{{schema}}
""")

REFORMAT_PROMPT_TEMPLATE = Template("""\
Reformat the following llm output:

{{ llm_output }}

So that it follows this schema:

{{ schema }}

Keep the contents intact. You may adjust key values to match the schema.
/nothink
""")


def extract_api_informations(place_object: dict) -> dict:
    return {
        "name": place_object["displayName"]["text"],
        "location": place_object["formattedAddress"],
        "rating": place_object.get("rating", None),
        "user_rating_count": place_object.get("userRatingCount", None),
        "opening_hours": place_object.get("regularOpeningHours", {}).get("weekdayDescriptions", []),
        "price_range": f"{place_object['priceRange']['startPrice']['currencyCode']} {place_object['priceRange']['startPrice']['units']}-{place_object['priceRange']['endPrice']['units']}" if 'priceRange' in place_object else "NO INFO",
        "flags": {
            k: place_object[k]
            for k in [
                "allowsDogs",
                "curbsidePickup",
                "delivery",
                "dineIn",
                "goodForChildren",
                "goodForGroups",
                "goodForWatchingSports",
                "liveMusic",
                "menuForChildren",
                "parkingOptions",
                "paymentOptions",
                "outdoorSeating",
                "reservable",
                "restroom",
                "servesBeer",
                "servesBreakfast",
                "servesBrunch",
                "servesCocktails",
                "servesCoffee",
                "servesDessert",
                "servesDinner",
                "servesLunch",
                "servesVegetarianFood",
                "servesWine",
                "takeout",
            ]
            if k in place_object
        },
    }


def grab_photo_from_gmaps(photo_url, maxsize=800):
    img_name = sha256(photo_url.encode("utf-8")).hexdigest() + ".jpg"
    fullpath = os.path.join(CACHE_DIR, img_name)
    if os.path.exists(fullpath):
        with open(fullpath, "rb") as f:
            imgbytes = f.read()
        return imgbytes
    full_url = "https://places.googleapis.com/v1/" + photo_url + "/media"
    response = requests.get(
        full_url,
        params={
            "key": GMAPS_API_KEY,
            "maxHeightPx": maxsize,
            "maxWidthPx": maxsize,
            "skipHttpRedirect": True,
        },
    )
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

    return bytes(chunks)


def grab_photos_bytes(photos: list[dict]) -> list[bytes]:
    photobytes: list[bytes] = []
    for photo in photos:
        url = photo["name"]
        photobyte = grab_photo_from_gmaps(url)
        if photobyte is None:
            continue
        photobytes.append(photobyte)
    return photobytes


def save_cache(cache_path, cache_object):
    with open(cache_path, "w") as f:
        json.dump(cache_object, f, indent=2)


def consolidate_summaries(cafe_raw_features: dict) -> CafeProfile:
    llm_output = agent.run_sync(
        CONSOLIDATE_SUMMARIES_PROMPT.render(
            review_summary=cafe_raw_features["review_summary"],
            photo_summaries="\n".join(
                [f" - {v}" for v in cafe_raw_features["photos_summaries"].values()]
            ),
            schema=CafeProfile.model_json_schema(),
        )
    )
    usage = llm_output.usage()
    print(
        f"LLM used {usage.request_tokens} request and {usage.response_tokens} response tokens totalling {usage.total_tokens}"
    )
    consolidated_summary = llm_output.output
    return consolidated_summary


def non_cafe_processor(place_object: dict) -> GeneralProfile:
    return GeneralProfile(
        name=place_object["displayname"]["text"],
        location=place_object["formattedAddress"],
        primary_type=place_object["primaryTypeDisplayName"]["text"],
        types=place_object["types"],
        opening_hours=place_object["regularOpeningHours"]["weekdayDescriptions"],
    )


MAPPER = {
    "allowsDogs": "dog_friendly",
    "goodForChildren": "child_friendly",
    "goodForGroups": "group_friendly",
}


def merge_api_info_with_profile(profile: CafeProfile, api_info: dict) -> CafeProfile:
    profile.name = api_info["name"]
    profile.location = api_info["location"]
    profile.rating = api_info["rating"]
    profile.user_rating_count = api_info["user_rating_count"]
    profile.opening_hours = api_info["opening_hours"]
    profile.price_range = api_info["price_range"]
    for flag in api_info["flags"]:
        if flag.startswith("serves") and api_info["flags"][flag]:
            fnbopts = profile.food_and_beverages_options
            fnbopts.append(flag[6:].lower())
            profile.food_and_beverages_options = list(set(fnbopts))
        elif (
            flag in ["curbsidePickup", "delivery", "dineIn", "takeout"]
            and api_info["flags"][flag]
        ):
            ffopts = profile.fulfillment_methods
            ffopts.append(re.sub(r"([a-z])([A-Z])", r"\1_\2", flag).lower())
            profile.fulfillment_methods = list(set(ffopts))
        elif (
            flag in ["outdoorSeating", "reservable", "restroom"]
            and api_info["flags"][flag]
        ):
            fclopts = profile.facilities
            fclopts.append(re.sub(r"([a-z])([A-Z])", r"\1_\2", flag).lower())
            profile.facilities = list(set(fclopts))
        elif (
            flag
            in [
                "allowsDogs",
                "goodForChildren",
                "goodForGroups",
            ]
            and api_info["flags"][flag]
        ):
            fclopts = profile.facilities
            fclopts.append(MAPPER[flag])
            profile.facilities = list(set(fclopts))
        elif flag == "parkingOptions":
            for v in api_info["flags"][flag].values():
                if v:
                    fclopts = profile.facilities
                fclopts.append("parking")
                profile.facilities = list(set(fclopts))
                break
    return profile


def process_place(place_object: dict) -> CafeProfile:
    placeid = place_object["id"]
    fullcachepath = os.path.join(OUTPUT_DIR, f"{placeid}.json")
    print(f"Finding cache for {placeid}...")
    if os.path.exists(fullcachepath):
        with open(fullcachepath, "r") as f:
            cafe_raw_features = json.load(f)
        print("Cache found and loaded.")
    else:
        cafe_raw_features = dict()
        print("Cache not found.")
    if "api_info" not in cafe_raw_features:
        print("calculating API INFO...")
        api_info = extract_api_informations(place_object)
        cafe_raw_features["api_info"] = api_info
        save_cache(fullcachepath, cafe_raw_features)
    else:
        print("API INFO already calculated. skipping..")
    reviews = place_object["reviews"]
    photos = place_object["photos"]
    if "review_summary" not in cafe_raw_features:
        print("calculating review summary...")
        review_summary = process_reviews(reviews)
        cafe_raw_features["review_summary"] = review_summary
        save_cache(fullcachepath, cafe_raw_features)
    else:
        print("reviewsummary already calculated.. skipping..")
    photo_summaries = []
    print("calculating photos summaries...")
    for photo in photos:
        photo_identifier = sha256(photo["name"].encode("utf8")).hexdigest()
        if photo_identifier in cafe_raw_features.setdefault("photos_summaries", {}):
            print(f"Found photo summary for {photo_identifier}.. skipping..")
            photo_summary = cafe_raw_features["photos_summaries"][photo_identifier]
        else:
            print(f"Calculating photo summary for {photo_identifier}..")
            photo_bytes = grab_photo_from_gmaps(photo["name"])
            photo_summary = process_photo([photo_bytes])
            cafe_raw_features["photos_summaries"][photo_identifier] = photo_summary
            save_cache(fullcachepath, cafe_raw_features)
        photo_summaries.append(photo_summary)
    print("finished processing all photos")
    if "final_raw_summary" in cafe_raw_features:
        print("found already consolidated raw features..")
        consolidator_output = cafe_raw_features["final_raw_summary"]
    else:
        print("calculating consolidated summary..")
        consolidator_output = consolidate_summaries(cafe_raw_features)
        cafe_raw_features["final_raw_summary"] = consolidator_output
        save_cache(fullcachepath, cafe_raw_features)
        print("finished consolidated summary..")

    print("Reformatting..")
    reformat_output = reformat_agent.run_sync(
        REFORMAT_PROMPT_TEMPLATE.render(
            llm_output=remove_think_tokens(consolidator_output),
            schema=CafeProfile.model_json_schema(),
        )
    ).output
    reformat_output = merge_api_info_with_profile(
        reformat_output, cafe_raw_features["api_info"]
    )
    return reformat_output
