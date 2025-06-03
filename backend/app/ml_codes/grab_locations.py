import json
import requests

# LAT_LONG = (-6.174904869095269, 106.8271353670165)
# LATLONG[0],LAT_LONG[1]
API_KEY = 'AIzaSyBMM3_s3QjI-5LNDDB5xwZoG28i_OBC3ek'
api_key = 'AIzaSyBmugJei5MXFJu2525l8Bh6cPNJKUtWcS4'

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
            "X-Goog-Api-Key": API_KEY,
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


    return json.dumps(results.json(), indent=2)

def grab_locations_opportunity(lat, lng):
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
            "includedTypes": ["hospital", "schools", "offices", "universities", "hall", "gyms","malls", "markets", "hotels"],
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": 4000.0,
                }
            },
        },
    )


    return json.dumps(results.json(), indent=2)

def grab_distance(start_lat, start_lng ,dest_lat, dest_lng):
    """
    Function to grab locations of opportunities.
    Args:
    lat (float): Latitude of the location.
    lng (float): Longitude of the location. 
    Returns:
    str: JSON string containing the results of the API call.
    """
    
    results = requests.post(
        "https://routes.googleapis.com/directions/v2:computeRoutes",
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
        },
        json={
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": start_lat,
                        "longitude":start_lng
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": dest_lat,
                        "longitude": dest_lng
                    }
                }
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": False,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "languageCode": "en-US",
            "units": "METRIC"
        }
    )


    return json.dumps(results.json(), indent=2)



def grab_address(location):
    lat, lng = location['lat'], location['lng']  # Jakarta
    # api_key = 'AIzaSyBmugJei5MXFJu2525l8Bh6cPNJKUtWcS4'

    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}'
    response = requests.get(url)
    data = response.json()

    address = data['results'][0]['formatted_address']
    return address
# with open("data/top-10.json", "w") as f:
#     json.dump(results.json(), f, indent=2)
    

