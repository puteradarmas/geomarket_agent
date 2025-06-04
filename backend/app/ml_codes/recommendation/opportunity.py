import os
from schemas import GeneralProfile, UserQuery
from jinja2 import Template
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from grab_locations import grab_distance

llm = GeminiModel(
    "gemini-2.0-flash",
    provider=GoogleGLAProvider(api_key="AIzaSyCeSFDojYhLttdSUP2wgFkjiTHqrNptXfQ"),
)

agent: Agent[None, str] = Agent(llm, output_type=str)

OPPORTUNITY_ANALYSIS_PROMPT = Template("""\
<role>
You are a professional market and location analyst. 
Given a location coordinate, you will perform an analysis of the surrounding locations.
Help the user analyze surrounding locations to determine the ideal plan for building a cafe.
</role>
<instruction>
Follow these steps to chunk and breakdown your task.

First, you need to make an analysis of the surrounding locations.
Put this in the `observation` part of the output.
For each location:
1. Determine the likely demographic of the surrounding area.
2. Derive their probably active hours, and their most likely time to visit.
3. Derive their probable unmet needs that we can cater to.
4. Derive their probable activity patterns and what we can provide to attract them.

Afterwards, consolidate all the informations above and make an analysis focusing on the following aspects to generate the `final_answer`.
- Target demographics; Which specific demographic can we target? All the following analysis will be based on this.
- Suggested concept and theme; What kind of cafe might best fit this target demography? List at most 10 possible concepts along with the reasoning for each concepts.
- Fullfillment methods; Should this cafe be primarily dine in? Should this cafe focus on other options like curbside pickups, takeouts, etc.
- Facilities and other experience enhancers; Determine the amenities you can provide to meet the possible demand of surrounding demographics, include the reasoning for each facilities.
- Operating factors; Based on the predicted active hours and probable traffic patterns surrounding the area. For example workflows, ordering methods, staffing model, operational hours, etc.
- Pricing level; Self explanatory

Separate your `observation` from your `final_answer`. Use the provided template below.
</instruction>
<answer_format>
You have been given 2 empty XML tags below, `observation` and `final_answer`.
format your observation and answer by putting them in the given XML tags.
</answer_format>
<inputs>
The following is the descriptions of the opportunities surrounding in your area.

{{ opportunities }}
</inputs>
<reasoning>
YOUR REASONING GOES HERE
</reasoning>
<final_answer>
YOUR FINAL ANSWER GOES HERE
</final_answer>
""")


def describe_opportunity(opportunity: GeneralProfile) -> str:
    all_descriptions = []
    all_descriptions.append(f"{opportunity.name} is a {opportunity.type}.")
    if opportunity.distance_to_point:
        all_descriptions.append("Travel routes to our location:")
        for distance in opportunity.distance_to_point:
            mode, distancemeters, duration = distance
            all_descriptions.append(f" - {mode}: {distancemeters} away, duration: {duration}.")
    all_descriptions.append("Operational hours:")
    all_descriptions.extend([f" - {oh}" for oh in opportunity.opening_hours])
    if opportunity.summaries:
        all_descriptions.append("Some summaries of the place:")
        all_descriptions.extend([f" - {s}" for s in opportunity.summaries])
    return "\n".join(all_descriptions)
    


def generate_opportunity_analysis(
    opportunities_list: list[GeneralProfile], user_query: UserQuery
) -> str:
    for opportunity in opportunities_list:
        if not opportunity.distance_to_point:
            opportunity.distance_to_point = grab_distance(
                opportunity.latlong[0], 
                opportunity.latlong[1], 
                user_query.latlong[0],
                user_query.latlong[1]
            )
    opportunities_string = [describe_opportunity(opp) for opp in opportunities_list]
    analysis_result = agent.run_sync(
        OPPORTUNITY_ANALYSIS_PROMPT.render(
            opportunities="\n".join(opportunities_string)
        )
    ).output
    return analysis_result
    
        
