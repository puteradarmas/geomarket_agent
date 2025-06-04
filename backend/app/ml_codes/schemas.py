from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field


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
    UNAVAILABLE = "unavailable"
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
    UNAVAILABLE = "unavailable"
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

class UserQuery(BaseModel):
    description: str
    latlong: list[float, float] = None

class GeneralProfile(BaseModel):
    name: str
    type: str
    latlong: list[float, float]
    opening_hours: list[str]
    summaries: list[str]
    distance_to_point: list[tuple[str, str, str]] = []

class CafeProfile(BaseModel):
    # Core Identification
    name: Optional[str] = None
    latlong: Optional[list[float, float]] = None
    location: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5, validate_default=False, allow_inf_nan=True)
    user_rating_count: Optional[int] = Field(None, ge=0, validate_default=False, allow_inf_nan=True)
    opening_hours: Optional[list[str]] = None
    price_range: Optional[str] = None
    one_sentence_summary: Optional[str] = None

    # Service Offerings
    food_and_beverages_options: List[ServiceType] = Field(default_factory=list)
    fulfillment_methods: List[FulfillmentMethod] = Field(default_factory=list)

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
    work_friendly_features: List[str] = Field(
        default_factory=list
    )  # laptop_friendly, study_atmosphere

    # Service Experience
    service_style: Optional[ServiceStyle] = None
    typical_wait_time: Optional[WaitTime] = None
    staff_friendliness: Optional[QualityLevel] = None

    # Facilities & Amenities
    facilities: List[FacilityType] = Field(default_factory=list)

    # Operational Info

    class Config:
        use_enum_values = True
