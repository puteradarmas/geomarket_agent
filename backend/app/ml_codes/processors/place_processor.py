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

from app.ml_codes.processors.photo_processor import process_photo
from app.ml_codes.processors.review_processor import (
    process_reviews,
    remove_think_tokens,
)
from app.ml_codes.schemas import (
    CafeProfile,
    CafeProfileAndReasoning,
    GeneralProfile,
    filter_invalid_enums,
    get_fields_and_descriptions,
)
from app.ml_codes.agents import qwen_agent as agent
from app.envs import GMAPS_API_KEY


OUTPUT_DIR = "outputs/intermediate"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CACHE_DIR = "outputs/imgcache"
os.makedirs(CACHE_DIR, exist_ok=True)


CONSOLIDATE_SUMMARIES_PROMPT = Template("""\
# ROLE
You are a professional cafe analyst piecing together multiple informations about the same cafe into one unified structured information.
# INSTRUCTION
You will be given multiple summaries derived from differing sources. All of the summaries refer to the same cafe.
Your job is to consolidate these summaries into a unified summary. 
You will meet conflicts / differing information, use the provided merging strategy to tackle that.
Here are all of the informations you are asked to consolidate together:
```
{{ information_list }}
```
## MERGING STRATEGY 
Use the following strategy to merge values
- Values describing availability: as long as one information confirms it exists, it exists.
- Values describing quantity: do majority voting excluding the zero / null values. Always err upwards.
- Lists: merge all the lists together, keep unique values only

## RULES
Adhere to the following rules:
- Leave fields empty (give them a value of `null`) when you cannot find information about them.
- Do not try to assume or infer a missing information without a reliable indicator. No info means null.
- Only generate one final JSON object. This JSON object must follow the schema.

## INPUTS
Editorial summaries:
```
{{editorial_summaries}}
```
---
Review summary:
```
{{review_summary}}
```
---
Photo summaries:
```
{{photo_summaries}}
```
""")

ONE_SENTENCE_SUMMARIZER = Template("""\
Given the following summaries of a cafe, please extract a summary that would describe the cafe.

General Summary:

{{general_summary}}

Editorial Summaries:

{{editorial_summaries}}

Review Summary:

{{review_summary}}

Photo Summaries:

{{photo_summaries}}

Keep the summary to just one sentence of 20-30 words. Your output must only be the one sentence summary and nothing else.
""")


def extract_api_informations(place_object: dict) -> dict:
    return {
        "name": place_object["displayName"]["text"],
        "location": place_object["formattedAddress"],
        "latlong": (
            place_object["location"]["latitude"],
            place_object["location"]["longitude"],
        )
        if "location" in place_object
        else None,
        "rating": place_object.get("rating", "NO INFO"),
        "user_rating_count": place_object.get("userRatingCount", "NO INFO"),
        "opening_hours": place_object.get("regularOpeningHours", {}).get(
            "weekdayDescriptions", []
        ),
        "price_range": f"{place_object['priceRange']['startPrice']['currencyCode']} {place_object['priceRange']['startPrice']['units']}-{place_object['priceRange']['endPrice']['units']}"
        if "priceRange" in place_object
        else "NO INFO",
        "editorialSummary": place_object.get("editorialSummary", {}).get("text", ""),
        "generativeSummary": place_object.get("generativeSummary", {})
        .get("overview", {})
        .get("text", ""),
        "reviewSummary": place_object.get("reviewSummary", {})
        .get("text", {})
        .get("text", ""),
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


def persist_cache(cache_path, cache_object):
    with open(cache_path, "w") as f:
        json.dump(cache_object, f, indent=2)


def consolidate_summaries(cafe_raw_features: dict) -> CafeProfile:
    editorial_summaries = [
        cafe_raw_features["api_info"][key]
        for key in ["editorialSummary", "generativeSummary", "reviewSummary"]
        if cafe_raw_features["api_info"][key]
    ]
    editorial_summaries = (
        "EDITORIAL SUMMARIES UNAVAILABLE"
        if not len(editorial_summaries)
        else "\n".join([f" - {es}" for es in editorial_summaries])
    )
    full_prompt = CONSOLIDATE_SUMMARIES_PROMPT.render(
        editorial_summaries=editorial_summaries,
        review_summary=cafe_raw_features["review_summary"],
        photo_summaries="\n".join(
            [f" - {v}" for v in cafe_raw_features["photos_summaries"].values()]
        ),
        information_list=get_fields_and_descriptions(
            CafeProfile,
            exclude_fields=set(
                [
                    "name",
                    "latlong",
                    "location",
                    "rating",
                    "user_rating_count",
                    "opening_hours",
                    "price_range",
                    "one_sentence_summary",
                ]
            ),
        ),
    )
    llm_output = agent.run_sync(full_prompt, output_type=str)
    print(llm_output.all_messages()[-3:])
    exit()
    usage = llm_output.usage()
    print(
        f"LLM used {usage.request_tokens} request and {usage.response_tokens} response tokens totalling {usage.total_tokens}"
    )
    consolidated_summary = llm_output.output
    return consolidated_summary.profile


def process_opportunity(place_object: dict) -> GeneralProfile:
    editorialSummary = place_object.get("editorialSummary", {}).get("text", "")
    generativeSummary = (
        place_object.get("generativeSummary", {}).get("overview", {}).get("text", "")
    )
    reviewSummary = (
        place_object.get("reviewSummary", {}).get("text", {}).get("text", "")
    )
    all_summaries = [editorialSummary, generativeSummary, reviewSummary]
    return GeneralProfile(
        name=place_object["displayName"]["text"],
        type=place_object["primaryTypeDisplayName"]["text"],
        latlong=[
            place_object["location"]["latitude"],
            place_object["location"]["longitude"],
        ],
        opening_hours=place_object.get("regularOpeningHours", {}).get(
            "weekdayDescriptions", ["NO INFO"]
        ),
        summaries=[s for s in all_summaries if s != ""],
    )


MAPPER = {
    "allowsDogs": "dog_friendly",
    "goodForChildren": "child_friendly",
    "goodForGroups": "group_friendly",
}


def merge_api_info_with_profile(profile: CafeProfile, api_info: dict) -> CafeProfile:
    profile.name = api_info["name"]
    profile.location = api_info["location"]
    profile.latlong = api_info["latlong"]
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


def extract_json_objects(text, decoder=json.JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data

    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.

    """
    pos = 0
    while True:
        match = text.find("{", pos)
        print(match)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            print(result)
            yield result
            pos = match + index
        except Exception as ex:
            print(ex)
            pos = match + 1


def attempt_json_parse(llm_output: str, desperate: bool = False) -> CafeProfile:
    llm_output = remove_think_tokens(llm_output)
    json_objects = []
    for json_object in extract_json_objects(llm_output):
        json_objects.append(json_object)
    if not json_objects:
        raise ValueError("Cannot find json in output")
    parsed_objects = []
    for jsobj in json_objects:
        try:
            if "rating" in jsobj and jsobj["rating"] == -1:
                jsobj["rating"] = None
            if "user_rating_count" in jsobj and jsobj["user_rating_count"] == -1:
                jsobj["user_rating_count"] = None
            with filter_invalid_enums(desperate):
                parsed_object = CafeProfile.model_validate(jsobj)
            parsed_objects.append(parsed_object)
        except Exception as ex:
            print(ex)
            continue
    if len(parsed_objects) != 1:
        print(json_objects)
        raise ValueError(f"Found {len(parsed_objects)} object instead of just 1")
    return parsed_objects[0]


def create_general_summary(generated_profile: CafeProfile) -> str:
    profile_obj = generated_profile.model_dump(mode="json")
    all_summaries = []
    all_summaries.append(
        f"Cafe name: {profile_obj['name']}. Location: {profile_obj['location']}."
    )
    if (rating := profile_obj["rating"] is not None) and (
        urc := profile_obj["user_rating_count"] is not None
    ):
        all_summaries.append(f" Rating: {rating}/5 from {urc} reviewers.")

    for key in [
        "price_range",
        "food_and_beverages_options",
        "fulfillment_methods",
        "capacity_size",
        "seating_types",
        "spacing_level",
        "decor_styles",
        "lighting_style",
        "noise_level",
        "wifi_quality",
        "power_outlet_availability",
        "work_friendly_features",
        "service_style",
        "typical_wait_time",
        "staff_friendliness",
        "facilities",
    ]:
        if value := profile_obj[key]:
            if type(value) is list:
                all_summaries.append(f"{key.replace('_', ' ')}: [{','.join(value)}]")
            else:
                all_summaries.append(f"{key.replace('_', ' ')}: {value}")
    return " ".join(all_summaries)


def generate_place_summary(
    cafe_raw_features: dict, generatedprofile: CafeProfile
) -> str:
    editorial_summaries = [
        cafe_raw_features["api_info"][key]
        for key in ["editorialSummary", "generativeSummary", "reviewSummary"]
        if cafe_raw_features["api_info"][key]
    ]
    editorial_summaries = (
        "EDITORIAL SUMMARIES UNAVAILABLE"
        if not len(editorial_summaries)
        else "\n".join([f" - {es}" for es in editorial_summaries])
    )
    general_summary = create_general_summary(generatedprofile)
    photo_summaries = "\n".join(
        [f" - {v}" for v in cafe_raw_features["photos_summaries"].values()]
    )

    llm_result = agent.run_sync(
        ONE_SENTENCE_SUMMARIZER.render(
            general_summary=general_summary,
            editorial_summaries=editorial_summaries,
            review_summary=cafe_raw_features["review_summary"],
            photo_summaries=photo_summaries,
        )
    )
    place_summary = remove_think_tokens(llm_result.output)
    return place_summary


def process_competitor_place(
    place_object: dict, max_reformat_attempts: int = 3
) -> CafeProfile:
    placeid = place_object["id"]
    fullcachepath = os.path.join(OUTPUT_DIR, f"{placeid}.json")
    print(f"Finding cache for {placeid}...")
    if os.path.exists(fullcachepath):
        print(fullcachepath)
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
        persist_cache(fullcachepath, cafe_raw_features)
    else:
        print("API INFO already calculated. skipping..")
    reviews = place_object["reviews"]
    photos = place_object["photos"]
    if "review_summary" not in cafe_raw_features:
        print("calculating review summary...")
        review_summary = process_reviews(reviews)
        cafe_raw_features["review_summary"] = review_summary
        persist_cache(fullcachepath, cafe_raw_features)
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
            persist_cache(fullcachepath, cafe_raw_features)
        photo_summaries.append(photo_summary)
    print("finished processing all photos")
    if "final_raw_summary" in cafe_raw_features:
        print("found already consolidated raw features..")
        consolidator_output = cafe_raw_features["final_raw_summary"]
    else:
        print("calculating consolidated summary..")
        consolidator_output = consolidate_summaries(cafe_raw_features)
        cafe_raw_features["final_raw_summary"] = dict(consolidator_output)
        persist_cache(fullcachepath, cafe_raw_features)
        print("finished consolidated summary..")

    parsed_output = merge_api_info_with_profile(
        consolidator_output, cafe_raw_features["api_info"]
    )

    if "one_sentence_summary" not in cafe_raw_features:
        one_sentence_summary = generate_place_summary(cafe_raw_features, parsed_output)
        cafe_raw_features["one_sentence_summary"] = one_sentence_summary
        persist_cache(fullcachepath, cafe_raw_features)
    else:
        one_sentence_summary = cafe_raw_features["one_sentence_summary"]

    parsed_output.one_sentence_summary = one_sentence_summary

    return parsed_output
