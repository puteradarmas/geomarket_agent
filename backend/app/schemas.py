from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

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
        
class request_schema(BaseModel):
    lat: float
    lgn: float
    address: Optional[str] = None
    additional_prompts: Optional[str] = None
    reccommendation_result: str
    
    
    
    
class FoodType(str, Enum):
    LIGHT_BITES = "light bites"
    RICE_BASED = "rice based meals"
    NOODLES_BASED = "noodle based meals"
    WESTERN = "western food"
    KOREAN = "korean food"
    JAPANESE = "japanese food"
    CHINESE = "chinese food"
    ASIAN = "asian food"
    OTHERS = "other types"

class DrinkType(str, Enum):
    COFFEE = "coffee"
    TEA = "tea"
    DAIRY = "dairy"
    JUICE = "juice"
    REFRESHING_DRINKS = "refreshing drinks"
    OTHERS = "other types"

class MenuItem(BaseModel):
    name: str
    price: Optional[int] = None
    item_type: list[FoodType | DrinkType]
    
class MenuObservation(BaseModel):
    menu_items: list[MenuItem]

class DesignObservation(BaseModel):
    theme_and_branding: str = Field(description="the kind of theme / branding the data suggests")
    layout_and_flow: str = Field(description="how the space is organized and zoned functionally or otherwise")
    visual_identity: str = Field(description="description of color palette, tones, brand color integration, visual consistency")
    atmosphere: str = Field(description="the atmosphere the space creates")
    lighting: str = Field(description="lighting strategy of the space")
    seating_arrangement: str = Field(description="how is seating organized (Examples: 2 person, large groups, large shared tables, private counters)")
    furniture_choice: str = Field(description="types of furnitures used for seating")
    materials_and_textures: str = Field(description="The tactile and visual materials used throughout the space that communicates the brand/theme")
    decorative_elements: str = Field(description="decorative elements used to reinforce theme")
    

class WFCFriendlinessObservation(BaseModel):
    wifi_quality: str = Field(description="availability and quality of the wifi")
    power_outlets: str = Field(description="power outlet availability")
    atmosphere_compatibility: str = Field(description="how suitable is the atmosphere for work based on the reviews")
    wfc_complaints: str = Field(description="complaints related to wfc from reviews")
    

class ServiceObservation(BaseModel):
    waiting_time: str = Field(description="qualitative (ex: quick, moderate, long) or quantitative (ex: under 15 mins, around 20-3 minutes) description of the waiting time")
    service_model: list[str] = Field(description="ordering methods")
    facilities: list[str] = Field(description="facilities mentioned or visible")


class CompetitorCafeObservation(BaseModel):
    menu_profile: MenuObservation
    design_profile: DesignObservation
    wfc_friendliness_profile: WFCFriendlinessObservation
    service_profile: ServiceObservation
    