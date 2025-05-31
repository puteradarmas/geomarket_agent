import json
import requests

LAT_LONG = (-6.174904869095269, 106.8271353670165)

results = requests.post(
    "https://places.googleapis.com/v1/places:searchNearby",
    headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": "AIzaSyBMM3_s3QjI-5LNDDB5xwZoG28i_OBC3ek",
        "X-Goog-FieldMask": ",".join([
            "places.accessibilityOptions",
            "places.attributions",
            "places.businessStatus",
            "places.containingPlaces",
            "places.displayName",
            "places.formattedAddress",
            "places.googleMapsLinks",
            "places.googleMapsUri",
            "places.id",
            "places.location",
            "places.photos",
            "places.postalAddress",
            "places.primaryType",
            "places.primaryTypeDisplayName",
            "places.pureServiceAreaBusiness",
            "places.shortFormattedAddress",
            "places.types",
            "places.priceLevel",
            "places.priceRange",
            "places.rating",
            "places.regularOpeningHours",
            "places.userRatingCount",
            "places.websiteUri",
            "places.allowsDogs",
            "places.curbsidePickup",
            "places.delivery",
            "places.dineIn",
            "places.editorialSummary",
            "places.generativeSummary",
            "places.goodForChildren",
            "places.goodForGroups",
            "places.goodForWatchingSports",
            "places.liveMusic",
            "places.menuForChildren",
            "places.neighborhoodSummary",
            "places.parkingOptions",
            "places.paymentOptions",
            "places.outdoorSeating",
            "places.reservable",
            "places.restroom",
            "places.reviews",
            "places.reviewSummary",
        ]),
    },
    json={
        "includedTypes": ["cafe", "coffee_shop"],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": LAT_LONG[0], "longitude": LAT_LONG[1]},
                "radius": 1500.0,
            }
        },
    },
)

with open("data/top-10.json", "w") as f:
    json.dump(results.json(), f, indent=2)
