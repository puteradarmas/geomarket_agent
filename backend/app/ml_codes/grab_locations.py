import json
import requests

API_KEY = "AIzaSyBMM3_s3QjI-5LNDDB5xwZoG28i_OBC3ek"
ROUTES_API_KEY = "AIzaSyBmugJei5MXFJu2525l8Bh6cPNJKUtWcS4"


def grab_locations_competitor(lat, lng, radius=4000.0):
    """
    Function to grab locations of competitors (cafes and coffee shops) near a given latitude and longitude.
    Args:
    lat (float): Latitude of the location.
    lng (float): Longitude of the location.
    Returns:
    str: JSON string containing the results of the API call.
    """

    results = requests.post(
        "https://places.googleapis.com/v1/places:searchNearby",
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": ",".join(
                [
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
                ]
            ),
        },
        json={
            "includedTypes": ["cafe", "coffee_shop"],
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": radius,
                }
            },
        },
    )

    return json.dumps(results.json(), indent=2)


def grab_locations_opportunity(lat, lng, radius=4000.0):
    """
    Function to grab locations of opportunities.
    Args:
    lat (float): Latitude of the location.
    lng (float): Longitude of the location.
    Returns:
    str: JSON string containing the results of the API call.
    """

    results = requests.post(
        "https://places.googleapis.com/v1/places:searchNearby",
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": ",".join(
                [
                    "places.businessStatus",
                    "places.displayName",
                    "places.id",
                    "places.location",
                    "places.primaryType",
                    "places.primaryTypeDisplayName",
                    "places.types",
                    "places.regularOpeningHours",
                    "places.editorialSummary",
                    "places.generativeSummary",
                    "places.reviewSummary",
                ]
            ),
        },
        json={
            "includedTypes": [
                "corporate_office",
                "university",
                "school",
                "library",
                "transit_station",
                "shopping_mall",
                "hotel",
                "book_store",
                "hospital",
                "government_office"
            ],
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": radius,
                }
            },
        },
    )

    return json.dumps(results.json(), indent=2)


def grab_distance(start_lat, start_lng, dest_lat, dest_lng):
    """
    Function to grab locations of opportunities.
    Args:
    lat (float): Latitude of the location.
    lng (float): Longitude of the location.
    Returns:
    str: JSON string containing the results of the API call.
    """
    distances = []
    for travelMode in ["DRIVE", "WALK", "TWO_WHEELER"]:
        results = requests.post(
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": ROUTES_API_KEY,
                "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
            },
            json={
                "origin": {
                    "location": {"latLng": {"latitude": start_lat, "longitude": start_lng}}
                },
                "destination": {
                    "location": {"latLng": {"latitude": dest_lat, "longitude": dest_lng}}
                },
                "travelMode": travelMode,
                "routingPreference": "TRAFFIC_AWARE",
                "computeAlternativeRoutes": False,
                "routeModifiers": {
                    "avoidTolls": False,
                    "avoidHighways": False,
                    "avoidFerries": False,
                },
                "languageCode": "en-US",
                "units": "METRIC",
            },
        )
        if results.status_code != 200:
            continue
        routes = results.json()["routes"]
        if not routes:
            continue
        route = routes[0]
        distance_meters = f"{route['distanceMeters']} meters"
        duration = route["duration"]
        distances.append((travelMode, distance_meters, duration))

    return distances
