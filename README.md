# geomarket_agent
An WebApp for learning the risk and potential of a location powered by LLM models.

**Install and Develop it on your Local Machine**

If you want to work locally using your own machine, you can clone this repo and push changes. Make sure practice a good pull and push action.

It requires npm and python both requirement provided in the repo.

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project python backend directory.
cd <YOUR_PROJECT_NAME>/backend

# Step 3: Install Python Requirements.
pip install -r /path/to/requirements.txt

# Step 4: Navigate to FrontEnd the project directory.
cd <YOUR_PROJECT_NAME>/frontend

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
# Step 4.1: Open one terminal for backend
cd <YOUR_PROJECT_NAME>/backend
python manage.py runserver

# Step 4.2: Open one terminal for frontend
cd <YOUR_PROJECT_NAME>/frontend
npm run dev
```

## Agents Flow and Structure

This project follows the following flow:
1. User provides details about their business location / just a location.
2. An agent searches nearby location of the same business type. The agent will also determine possible target demographic and scan the nearby location for such places.
3. Each locations will be scanned. A separate agent (or just an LLM call) will be used to generate a quick summary / parameter of each locations. Call this `data processing agent`.
4. After processing all locations, another agent will identify patterns / similarities / opportunities.
5. Finally, a report will be generated containing insights and recommendations.

## Data Processing Agent

### Input
Takes as an input a `Place` Object returned from calling the google maps API. Each `Place` Object has information with varying levels of semantic richness. Consult the [official docs](https://developers.google.com/maps/documentation/places/web-service/nearby-search) for a full overview and details about each information.

We take as input non-abstract fields such as
- `allowsDogs`
- `servesCoffee`
- `rating`
- `opening hours`
- `priceLevel`

as well as highly abstract fields
- reviews; a bunch of review in natural language
- photos; a bunch of pictures taken in the location

### Output
We standardize the output into a pydantic schema as follows:
```py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class PriceLevel(str, Enum):
    BUDGET = "budget"
    MODERATE = "moderate"
    EXPENSIVE = "expensive"
    VERY_EXPENSIVE = "very_expensive"

class ServiceType(str, Enum):
    COFFEE = "coffee"
    BREAKFAST = "breakfast"
    BRUNCH = "brunch"
    LUNCH = "lunch"
    DINNER = "dinner"
    DESSERT = "dessert"
    BEER = "beer"
    WINE = "wine"
    COCKTAILS = "cocktails"
    VEGETARIAN = "vegetarian"

class FulfillmentMethod(str, Enum):
    DINE_IN = "dine_in"
    TAKEOUT = "takeout"
    DELIVERY = "delivery"
    CURBSIDE_PICKUP = "curbside_pickup"

class QualityLevel(str, Enum):
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"

class CapacitySize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class SeatingType(str, Enum):
    COUNTER = "counter"
    TABLES = "tables"
    COUCHES = "couches"
    COMMUNAL = "communal"
    BOOTHS = "booths"

class DecorStyle(str, Enum):
    INDUSTRIAL = "industrial"
    MODERN = "modern"
    RUSTIC = "rustic"
    ECLECTIC = "eclectic"
    MINIMALIST = "minimalist"

class NoiseLevel(str, Enum):
    SILENT = "silent"
    QUIET = "quiet"
    MODERATE = "moderate"
    NOISY = "noisy"
    LOUD = "loud"

class LightingStyle(str, Enum):
    BRIGHT = "bright"
    DIM = "dim"
    NATURAL = "natural"
    MIXED = "mixed"

class ServiceStyle(str, Enum):
    COUNTER = "counter"
    TABLE = "table"
    SELF_SERVE = "self_serve"
    MIXED = "mixed"

class WaitTime(str, Enum):
    FAST = "fast"
    QUICK = "quick"
    MODERATE = "moderate"
    SLOW = "slow"

class AvailabilityLevel(str, Enum):
    NONE = "none"
    LIMITED = "limited"
    GOOD = "good"
    ABUNDANT = "abundant"

class SpacingLevel(str, Enum):
    CRAMPED = "cramped"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"

class FacilityType(str, Enum):
    OUTDOOR_SEATING = "outdoor_seating"
    PARKING = "parking"
    RESTROOM = "restroom"
    ACCESSIBLE = "accessible"
    DOG_FRIENDLY = "dog_friendly"
    CHILD_FRIENDLY = "child_friendly"
    GROUP_FRIENDLY = "group_friendly"
    RESERVABLE = "reservable"
    LOYALTY_PROGRAM = "loyalty_program"
    PRAYER_ROOM = "prayer_room"
    CHARGING_STATIONS = "charging_stations"
    BOOKSHELF = "bookshelf"
    GAME_AREA = "game_area"

class CafeProfile(BaseModel):
    # Core Identification
    name: str
    location: str
    rating: Optional[float] = Field(ge=0, le=5)
    user_rating_count: Optional[int] = Field(ge=0)
    
    # Service Offerings
    service_types: List[ServiceType] = Field(default_factory=list)
    fulfillment_methods: List[FulfillmentMethod] = Field(default_factory=list)
    price_level: Optional[PriceLevel] = None
    
    # Physical Space
    capacity_size: Optional[CapacitySize] = None
    seating_types: List[SeatingType] = Field(default_factory=list)
    spacing_level: Optional[SpacingLevel] = None
    
    # Ambience Characteristics
    decor_styles: List[DecorStyle] = Field(default_factory=list)
    lighting_style: Optional[LightingStyle] = None
    noise_level: Optional[NoiseLevel] = None
    
    # Work Environment
    wifi_quality: Optional[QualityLevel] = None
    power_outlet_availability: Optional[AvailabilityLevel] = None
    work_friendly_features: List[str] = Field(default_factory=list)  # laptop_friendly, study_atmosphere
    
    # Service Experience
    service_style: Optional[ServiceStyle] = None
    typical_wait_time: Optional[WaitTime] = None
    staff_friendliness: Optional[QualityLevel] = None
    
    # Facilities & Amenities
    facilities: List[FacilityType] = Field(default_factory=list)
    
    # Operational Info
    opening_hours: Optional[dict] = None
    photos: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True
```

```json
{
    "$defs": {
        "AvailabilityLevel": {
            "enum": [
                "null",
                "limited",
                "good",
                "abundant"
            ],
            "title": "AvailabilityLevel",
            "type": "string"
        },
        "CapacitySize": {
            "enum": [
                "small",
                "medium",
                "large"
            ],
            "title": "CapacitySize",
            "type": "string"
        },
        "DecorStyle": {
            "enum": [
                "industrial",
                "modern",
                "rustic",
                "eclectic",
                "minimalist"
            ],
            "title": "DecorStyle",
            "type": "string"
        },
        "FacilityType": {
            "enum": [
                "outdoor_seating",
                "parking",
                "restroom",
                "accessible",
                "dog_friendly",
                "child_friendly",
                "group_friendly",
                "reservable",
                "loyalty_program",
                "prayer_room",
                "charging_stations",
                "bookshelf",
                "game_area"
            ],
            "title": "FacilityType",
            "type": "string"
        },
        "FulfillmentMethod": {
            "enum": [
                "dine_in",
                "takeout",
                "delivery",
                "curbside_pickup"
            ],
            "title": "FulfillmentMethod",
            "type": "string"
        },
        "LightingStyle": {
            "enum": [
                "bright",
                "dim",
                "natural",
                "mixed"
            ],
            "title": "LightingStyle",
            "type": "string"
        },
        "NoiseLevel": {
            "enum": [
                "silent",
                "quiet",
                "moderate",
                "noisy",
                "loud"
            ],
            "title": "NoiseLevel",
            "type": "string"
        },
        "PriceLevel": {
            "enum": [
                "budget",
                "moderate",
                "expensive",
                "very_expensive"
            ],
            "title": "PriceLevel",
            "type": "string"
        },
        "QualityLevel": {
            "enum": [
                "poor",
                "fair",
                "good",
                "excellent"
            ],
            "title": "QualityLevel",
            "type": "string"
        },
        "SeatingType": {
            "enum": [
                "counter",
                "tables",
                "couches",
                "communal",
                "booths"
            ],
            "title": "SeatingType",
            "type": "string"
        },
        "ServiceStyle": {
            "enum": [
                "counter",
                "table",
                "self_serve",
                "mixed"
            ],
            "title": "ServiceStyle",
            "type": "string"
        },
        "ServiceType": {
            "enum": [
                "coffee",
                "breakfast",
                "brunch",
                "lunch",
                "dinner",
                "dessert",
                "beer",
                "wine",
                "cocktails",
                "vegetarian"
            ],
            "title": "ServiceType",
            "type": "string"
        },
        "SpacingLevel": {
            "enum": [
                "cramped",
                "comfortable",
                "spacious"
            ],
            "title": "SpacingLevel",
            "type": "string"
        },
        "WaitTime": {
            "enum": [
                "fast",
                "quick",
                "moderate",
                "slow"
            ],
            "title": "WaitTime",
            "type": "string"
        }
    },
    "properties": {
        "name": {
            "title": "Name",
            "type": "string"
        },
        "location": {
            "title": "Location",
            "type": "string"
        },
        "rating": {
            "anyOf": [
                {
                    "maximum": 5,
                    "minimum": 0,
                    "type": "number"
                },
                {
                    "type": "null"
                }
            ],
            "title": "Rating"
        },
        "user_rating_count": {
            "anyOf": [
                {
                    "minimum": 0,
                    "type": "integer"
                },
                {
                    "type": "null"
                }
            ],
            "title": "User Rating Count"
        },
        "service_types": {
            "items": {
                "$ref": "#/$defs/ServiceType"
            },
            "title": "Service Types",
            "type": "array"
        },
        "fulfillment_methods": {
            "items": {
                "$ref": "#/$defs/FulfillmentMethod"
            },
            "title": "Fulfillment Methods",
            "type": "array"
        },
        "price_level": {
            "anyOf": [
                {
                    "$ref": "#/$defs/PriceLevel"
                },
                {
                    "type": "null"
                }
            ],
            "default": null
        },
        "capacity_size": {
            "anyOf": [
                {
                    "$ref": "#/$defs/CapacitySize"
                },
                {
                    "type": "null"
                }
            ],
            "default": null
        },
        "seating_types": {
            "items": {
                "$ref": "#/$defs/SeatingType"
            },
            "title": "Seating Types",
            "type": "array"
        },
        "spacing_level": {
            "anyOf": [
                {
                    "$ref": "#/$defs/SpacingLevel"
                },
                {
                    "type": "null"
                }
            ],
            "default": null
        },
        "decor_styles": {
            "items": {
                "$ref": "#/$defs/DecorStyle"
            },
            "title": "Decor Styles", "type": "array"
        },
        "lighting_style": {
            "anyOf": [
                {
                    "$ref": "#/$defs/LightingStyle"
                },
                {
                    "type": "null"
                }
            ],
            "default": null
        },
        "noise_level": {
            "anyOf": [
                {
                    "$ref": "#/$defs/NoiseLevel"
                },
                {
                    "type": "null"
                }
            ],
            "default": null
        },
        "wifi_quality": {
            "anyOf": [
                {
                    "$ref": "#/$defs/QualityLevel"
                },
                {
                    "type": "null"
                }
            ],
            "default": null
        },
        "power_outlet_availability": {
            "anyOf": [
                {
                    "$ref": "#/$defs/AvailabilityLevel"
                },
                {
                    "type": "null"
                }
            ],
            "default": null
        },
        "work_friendly_features": {
            "items": {
                "type": "string"
            },
            "title": "Work Friendly Features",
            "type": "array"
        },
        "service_style": {
            "anyOf": [
                {
                    "$ref": "#/$defs/ServiceStyle"
                },
                {
                    "type": "null"
                }
            ],
            "default": null
        },
        "typical_wait_time": {
            "anyOf": [
                {
                    "$ref": "#/$defs/WaitTime"
                },
                {
                    "type": "null"
                }
            ],
            "default": null
        },
        "staff_friendliness": {
            "anyOf": [
                {
                    "$ref": "#/$defs/QualityLevel"
                },
                {
                    "type": "null"
                }
            ],
            "default": null
        },
        "facilities": {
            "items": {
                "$ref": "#/$defs/FacilityType"
            },
            "title": "Facilities",
            "type": "array"
        },
        "opening_hours": {
            "anyOf": [
                {
                    "additionalProperties": true,
                    "type": "object"
                },
                {
                    "type": "null"
                }
            ],
            "default": null,
            "title": "Opening Hours"
        },
        "photos": {
            "items": {
                "type": "string"
            },
            "title": "Photos",
            "type": "array"
        }
    },
    "required": [
        "name",
        "location",
        "rating",
        "user_rating_count"
    ],
    "title": "CafeProfile",
    "type": "object"
}
```

### Process
non-abstract fields are extracted and selected before being merged into a more condensed representations. Abstract fields such as `reviews` and `photos` are processed by LLMs to extract observable predetermined keywords. All of this are ultimately merged together.

