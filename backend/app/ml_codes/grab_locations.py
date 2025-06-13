import json
import requests
from app.envs import GMAPS_API_KEY, ROUTES_API_KEY



def grab_locations_competitor(lat, lng):
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
            "X-Goog-Api-Key": GMAPS_API_KEY,
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
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": 4000.0,
                }
            },
        },
    )


    return results.json()

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
            "X-Goog-Api-Key": GMAPS_API_KEY,
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
    return results.json()

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



def grab_address(location):
    lat, lng = location['lat'], location['lng']  # Jakarta

    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={ROUTES_API_KEY}'
    response = requests.get(url)
    data = response.json()

    address = data['results'][0]['formatted_address']
    return address
    

