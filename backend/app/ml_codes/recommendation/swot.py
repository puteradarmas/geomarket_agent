from app.ml_codes.schemas import CafeProfile, UserQuery
from jinja2 import Template
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from app.ml_codes.grab_locations import grab_distance

from app.ml_codes.agents import gemini_agent

SWOT_ANALYSIS_TEMPLATE = Template("""\
<role>
You are a professional business analyst adept at making SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis.
You will make a SWOT analysis of several cafes against an opportunity analysis of an area.
</role>
<instruction>
You will be given the profiles of several cafes as an input along with a demographic analysis of an area.
For each cafe, you will output a swot analysis as follows:
 - Strengths: What advantages does this café have in relation to the opportunity analysis? Consider factors like brand image, customer loyalty, location, unique offerings, or ambiance.
 - Weaknesses: Where does the café fall short compared to the opportunity analysis of the area? Look at pricing, menu limitations, service quality, or visibility.
 - Opportunities: What trends or local factors can the café take advantage of? Consider emerging consumer preferences, nearby developments, or gaps in the competition.
 - Threats: What external challenges could impact this cafe's success in matching the opportunity analysis?
 
First output your thinking into the provided xml tag `thinking` below, then add the output to `output`.
</instruction>
<rules>
- Output must always be a JSON array. When only a single input is provided, the output must still be a JSON array with one member.
- Only one JSON object per cafe.
- Follow the format.
</rules>
<Inputs>
Cafe Profiles:
{{cafe_profiles}}

Opportunity Analysis:
{{opportunity_analysis}}
</Inputs>
<output_format>
[
    {
        "cafe_name": cafe_1,
        "strengths": ...,
        "weaknesses": ...,
        "opportunities": ...,
        "threats": ...,
    },
    {
        "cafe_name": cafe_2,
        "strengths": ...,
        "weaknesses": ...,
        "opportunities": ...,
        "threats": ...,
    }
    ...
    {
        "cafe_name": cafe_N,
        "strengths": ...,
        "weaknesses": ...,
        "opportunities": ...,
        "threats": ...,
    }
]
</output_format>
<thinking>
YOUR THINKING GOES HERE
</thinking>
<output>
YOUR OUTPUT GOES HERE
</output>
""")


GENERATE_SUMMARY_TEMPLATE = Template("""\
Given the following description of a cafe:

{{description}}

Extract the following parameters from the description:
 - concept of the cafe
 - operational hours
 - price range
 - targeted demogrphy
 - facilities and amenities
 - menu choice
 - ordering options (dine in, take out, curbside pickups, drive through, etc)
 
Make no assumptions. When an information is missing, then just say there is no information about it.
Condense them into a paragraph without any formattings.
""")

def create_cafe_summary(generated_profile: CafeProfile) -> str:
    profile_obj = generated_profile.model_dump(mode="json")
    all_summaries = []
    all_summaries.append(f"Cafe name: {profile_obj['name']}. Location: {profile_obj['location']}.")
    all_summaries.append(f"One sentence summary of the cafe: {profile_obj['one_sentence_summary']}.")
    if (rating:=profile_obj["rating"] is not None) and (urc:=profile_obj['user_rating_count'] is not None):
        all_summaries.append(f" Rating: {rating}/5 from {urc} reviewers.")
    if (open_hours:=profile_obj.get("opening_hours", None)) is not None:
        all_summaries.append(f"Opening hours: {[','.join(open_hours)]}.")
        
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
        "facilities"
    ]:
        if value:=profile_obj[key]:
            if type(value) is list:
                all_summaries.append(f"{key.replace('_', ' ')}: [{','.join(value)}].")
            else:
                all_summaries.append(f"{key.replace('_', ' ')}: {value}.")
    return ' '.join(all_summaries)

def generate_cafe_summary(user_query: UserQuery) -> str:
    cafe_description = user_query.description
    summary = gemini_agent.run_sync(
        GENERATE_SUMMARY_TEMPLATE.render(
            description=cafe_description
        )
    ).output
    return summary

def preprocess_subjects(subject_list: list[CafeProfile | UserQuery]) -> list[str]:
    preprocessed = []
    for subject in subject_list:
        if type(subject) is CafeProfile:
            preprocessed.append(
                create_cafe_summary(subject)
            )
        else:
            preprocessed.append(
                generate_cafe_summary(subject)
            )
    return preprocessed

def generate_swot_analysis(subject_list: list[CafeProfile | UserQuery], opportunity_summary: str) -> str:
    preprocessed_subjects = preprocess_subjects(subject_list)
    
    raw_swot_analysis = gemini_agent.run_sync(SWOT_ANALYSIS_TEMPLATE.render(
        cafe_profiles=preprocessed_subjects,
        opportunity_analysis=opportunity_summary
    )).output
    return raw_swot_analysis
    