import threading
from enum import Enum
from typing import List, Optional, Dict

from contextlib import contextmanager

from pydantic import BaseModel, Field, field_validator, ValidationError


class FilteringContext:
    _local = threading.local()
    
    @classmethod
    def set_filter_mode(cls, enabled: bool):
        """Enable or disable enum filtering globally"""
        cls._local.filter_invalid_enums = enabled
    
    @classmethod
    def is_filter_enabled(cls) -> bool:
        """Check if enum filtering is currently enabled"""
        return getattr(cls._local, 'filter_invalid_enums', False)

@contextmanager
def filter_invalid_enums(enabled: bool = True):
    """Context manager to temporarily enable/disable enum filtering"""
    original = FilteringContext.is_filter_enabled()
    FilteringContext.set_filter_mode(enabled)
    try:
        yield
    finally:
        FilteringContext.set_filter_mode(original)


class FilterableEnumModel(BaseModel):
    """Base model that supports toggleable enum filtering"""
    
    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Initialize the enum registry when subclass is created"""
        super().__init_subclass__(**kwargs)
        cls.enum_field_registry = {}
    
    @classmethod
    def register_enum_field(cls, field_name: str, enum_class: type):
        """Register a field as an enum list field"""
        if not hasattr(cls, 'enum_field_registry'):
            cls.enum_field_registry = {}
        cls.enum_field_registry[field_name] = enum_class
    
    @field_validator('*', mode='before')
    @classmethod
    def filter_enum_lists(cls, v, info):
        """Universal validator for all enum list fields"""
        field_name = info.field_name
        
        # Skip if filtering is disabled or this isn't a registered enum field
        if not FilteringContext.is_filter_enabled():
            return v
        
        registry = getattr(cls, 'enum_field_registry', {})
        if field_name not in registry:
            return v
            
        if isinstance(v, list):    
            enum_class = registry[field_name]
            valid_enum_values = set(item.value for item in enum_class)
            
            # Filter out invalid values
            valid_values = [item for item in v if item in valid_enum_values]
            return valid_values
        else:
            enum_class = registry[field_name]
            valid_enum_values = set(item.value for item in enum_class)
            if v not in valid_enum_values:
                return None 


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

class CafeProfile(FilterableEnumModel):
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

CafeProfile.register_enum_field("food_and_beverages_options", ServiceType)
CafeProfile.register_enum_field("fulfillment_methods", FulfillmentMethod)
CafeProfile.register_enum_field("seating_types", SeatingType)
CafeProfile.register_enum_field("decor_styles", DecorStyle)
CafeProfile.register_enum_field("facilities", FacilityType)
CafeProfile.register_enum_field("capacity_size", CapacitySize)
CafeProfile.register_enum_field("spacing_level", SpacingLevel)
CafeProfile.register_enum_field("lighting_style", LightingStyle)
CafeProfile.register_enum_field("noise_level", NoiseLevel)
CafeProfile.register_enum_field("wifi_quality", QualityLevel)
CafeProfile.register_enum_field("power_outlet_availability", AvailabilityLevel)
CafeProfile.register_enum_field("service_style", ServiceStyle)
CafeProfile.register_enum_field("typical_wait_time", WaitTime)
CafeProfile.register_enum_field("staff_friendliness", QualityLevel)
