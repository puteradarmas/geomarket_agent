import re
import json
import os
from jinja2 import Template
from schemas import GeneralProfile, CafeProfile, UserQuery
from recommendation.opportunity import generate_opportunity_analysis
from functools import partial
from recommendation.swot import generate_swot_analysis

from processors.place_processor import save_cache, extract_json_objects

from agents import gemini_agent

CACHE_DIR = "outputs/recommender_intermediate"
os.makedirs(CACHE_DIR, exist_ok=True)

GAP_ANALYSIS_PROMPT_TEMPLATE = Template("""
<role>
You are a senior business analyst specializing in retail and F&B gap analyses. Conduct a professional gap analysis for a cafe business using ONLY user-provided data. Never invent facts or make assumptions.
</role>

<instruction>
Follow the provided analysis framework and adhere to the output format provided below.
First, think and reason about each steps of your detailed analysis. Fill the `reasoning` tag provided below.
Afterwards, generate your final answer following the output format in the `output` tag.
</instruction>

<background_context>
The user is establishing/optimizing a cafe in a competitive area nearby cafes. You will receive:
1. Demographic analysis of the immediate area provided in `demographic_analysis`
2. SWOT analysis of the user's cafe concept, provided in `user_swot`
3. SWOTs analysis of competitor cafes, provide in `competitor_cafe_swots`
</background_context>

<rules>
- Strictly use only provided data - never invent or extrapolate
- State "Insufficient data: [missing element]" if inputs are incomplete
- Quantify comparisons using relative terms (e.g., "20% higher pricing")
- Prioritize actionable opportunities with clear exploitation paths
- Maintain neutral objectivity when analyzing all SWOTs
</rules>

<analysis_framework>
1. UNMET NEEDS: Identify demographic needs unaddressed by ANY cafe (including user's), supported by demographic data
2. POSITIONING: Compare user's concept vs competitors by comparing SWOTs strengths/weaknesses
3. VULNERABILITIES: Extract confirmed weaknesses from competitor SWOTs provided in `competitor_cafe_swots` and map to user's strengths provided in `user_swot`
4. FIT GAPS: Evaluate alignment between ALL cafes and demographic data
</analysis_framework>

<output_format>
<gap_analysis_report>
<report_title>Gap Analysis: [User's Cafe Name]</report_title>

<unmet_demographic_needs>
<identified_gaps>
- [Specific need] (Evidence: [Demographic data reference])
- [Specific need] (Evidence: [Demographic data reference])
</identified_gaps>
<competitor_coverage_gap>[Summary statement]</competitor_coverage_gap>
</unmet_demographic_needs>

<concept_positioning>
<strengths>[Advantage vs competitors] (Source: [User SWOT Strength])</strengths>
<weaknesses>[Disadvantage vs competitors] (Source: [User SWOT Weakness])</weaknesses>
<differentiation_score>[High/Medium/Low] based on uniqueness</differentiation_score>
</concept_positioning>

<competitor_vulnerabilities>
<vulnerability>
<competitor>[Competitor 1]</competitor>
<weakness>[Specific weakness]</weakness>
<opportunity>[Matching user strength]</opportunity>
</vulnerability>
<vulnerability>
<competitor>[Competitor 2]</competitor>
<weakness>[Specific weakness]</weakness>
<opportunity>[Matching user strength]</opportunity>
</vulnerability>
...
<vulnerability>
<competitor>[Competitor N]</competitor>
<weakness>[Specific weakness]</weakness>
<opportunity>[Matching user strength]</opportunity>
</vulnerability>
</competitor_vulnerabilities>

<demographic_fit_gaps>
<users_cafe_fit>
<alignment>[Aspect matching demographics]</alignment>
<misalignment>[Aspect conflicting demographics] (Source: [Data reference])</misalignment>
</users_cafe_fit>

<competitor_fit_summary>
<competitor name="[Competitor 1]">
<pricing_misalignment>[Description]</pricing_misalignment>
<experience_gaps>[Description]</experience_gaps>
<service_limitations>[Description]</service_limitations>
</competitor>
<competitor name="[Competitor 2]">
<pricing_misalignment>[Description]</pricing_misalignment>
<experience_gaps>[Description]</experience_gaps>
<service_limitations>[Description]</service_limitations>
</competitor>
...
<competitor name="[Competitor N]">
<pricing_misalignment>[Description]</pricing_misalignment>
<experience_gaps>[Description]</experience_gaps>
<service_limitations>[Description]</service_limitations>
</competitor>
</competitor_fit_summary>

<critical_gaps>[Shared weaknesses across all cafes]</critical_gaps>
</demographic_fit_gaps>

<strategic_recommendations>
<priority_opportunities>
1. [Actionable opportunity] (Targets: [Specific gap/weakness])
2. [Actionable opportunity] (Targets: [Specific gap/weakness])
...
N. [Actionable opportunity] (Targets: [Specific gap/weakness])
</priority_opportunities>
<concept_adjustments>[Data-backed operational changes]</concept_adjustments>
<risk_mitigation>[Critical user weaknesses to address]</risk_mitigation>
</strategic_recommendations>
</gap_analysis_report>
</output_format>

<user_inputs>

<demographic_analysis>
{{demographic_analysis}}
</demographic_analysis>

<user_swot>
{{user_swot}}
</user_swot>

<competitor_cafe_swots>
{{competitor_swot}}
</competitor_cafe_swots>
</user_inputs>
<reasoning>
FILL WITH YOUR REASONING
</reasoning>
<output>
YOUR FINAL ANSWER GOES HERE. FOLLOW THE FORMAT
</output>
""")

RECOMMENDATION_GENERATION_PROMPT_TEMPLATE = Template("""\
<role>
You are a professional business analyst. Having done your research, you are here to compile a final recommendation report.
</role>
<background>
You are handling a client's request. Given a location and their concept / idea for a cafe, you were tasked to gather information to ultimately compile an analysis of recommendations for the client.
Previously you have made several analysis of the cafe. These will be your input to make the recommendation report:
1. A demographics / opportunity analysis from analyzing the types of locations around a cafe location.
2. A gap analysis of how much the client's cafe fit the opportunity analysis, compared to its nearby competitors (other cafes). This gap analysis has already indirectly integrated the competitor's informations from making comparison.
3. A SWOT analysis of the client's cafe concept made against the opportunity analysis.
</background>
<instruction>
Compile the informations provided to create a recommendation report.
Follow the provided format to generate your report.
First reason and think out loud about each segments of the report, identify and analyze the relevant inputs to generate the analysis for each section. Enclose your reasoning in the provided `reasoning` XML tag below.
After you finished reasoning and feels satisfied, generate the report as your final answer, enclosed by `output` XML tags. Strictly follow the output format.
</instruction>
<output_format>
# Cafe Opportunity Analysis: [cafe name if provided]

## 1. Demographic Opportunity Snapshot
- Summary of target demographics
- Suggested concept and theme
- Fullfillment methods
- Facilities and other experience enhancers
- Operating factors
- Pricing level

## 2. Competitive Landscape
- Market gap analysis from the POV of the client's cafe
- Competitor vulnerability map
- Positioning of the client's concept

## 3. Strategic Recommendations
- A table with columns `Priority`, `Aspect`, `Action`, `Reasoning`
- Priority; [Low/Medium/High] 
- Aspect; [Concept / theme, service options, facilities, operating factors, pricing]
- Action; what is the recommended action to take?
- Reasoning; what is the reasoning behind the recommendation? Anchor this to the analysis you have made above

Example for (3):
| Priority | Aspect            | Action                          | Reasoning                                            |
|----------|-------------------|---------------------------------|------------------------------------------------------|
| High     | Operating factors | Open earlier starting from 6 AM | To cater to workers / university students commuting  |
</output_format>
<inputs>
<demographics_opportunity_analysis>
Below is the opportunity analysis based on the inferred demography of the area:
{{ demographics_opportunity_analysis }}
</demographics_opportunity_analysis>
<gap_analysis>
Below is the gap analysis done by comparing the SWOTs analysis of each cafes with each other. The SWOT is analyzed based on how each cafe fares against the opportunity analyzed above.
{{ gap_analysis }}
</gap_analysis>
<client_swot>
The SWOT of the client cafe:
{{ client_swot }}
</client_swot>
<client_competitors_swots>
The SWOTs of all of the competing cafes:
{{ competitor_swot }}
</client_competitors_swots>
</inputs>
<rules>
- The report must follow the above structure without any additions.
- Making up facts is unhelpful and harmful.
- Making up another format is also unhelpful and harmful.
</rules>
<reasoning>
YOUR REASONING GOES HERE.
</reasoning>
<output>
YOUR OUTPUT GOES HERE. FOLLOW THE MARKDOWN FORMAT PROVIDED ABOVE.
</output>
""")

def generate_gap_analysis(
    self_swot: str,
    competitor_swot: str,
    opportunity_summary: str
) -> str:
    full_prompt = GAP_ANALYSIS_PROMPT_TEMPLATE.render(
            demographic_analysis=opportunity_summary,
            user_swot=self_swot,
            competitor_swot=competitor_swot
        )
    print(f"===============================\nFULL PROMPT : \n\n {full_prompt} \n\n =======================================")
    gap_analysis_output = gemini_agent.run_sync(
        full_prompt
    ).output
    return gap_analysis_output

def generate_recommendations(
    gap_analysis: str,
    self_swot: list[dict],
    competitor_swot: list[dict],
    opportunity_summary: str
):  
    full_prompt = RECOMMENDATION_GENERATION_PROMPT_TEMPLATE.render(
        demographics_opportunity_analysis=opportunity_summary,
        gap_analysis=gap_analysis,
        client_swot=self_swot[0],
        competitor_swot=competitor_swot
    )
    print(f"===============================\nFULL PROMPT : \n\n {full_prompt} \n\n =======================================")
    recommendation_output = gemini_agent.run_sync(
        full_prompt
    ).output
    
    return recommendation_output

def grab_markdown(
    llm_output: str
) -> str:
    regex = r"^#{1} [\S ]+"
    content_matches = list(re.finditer(regex, llm_output, re.MULTILINE))
    assert len(content_matches) > 0, "Found NO markdown headers. Fix your shit"
    mtch = content_matches[0]
    unclean_markdown = llm_output[mtch.start():]
    return unclean_markdown
    
def grab_xml_tag(
    llm_output: str,
    tagname: str
) -> str:
    regex = rf"<{tagname}>(?:(?!<{tagname}>)[\s\S])*?<\/{tagname}>"
    content_matches = list(re.finditer(regex, llm_output, re.MULTILINE))
    assert len(content_matches) == 1, "Found more than one tags"
    mtch = content_matches[0]
    start, end = mtch.span()
    return llm_output[start:end][2+len(tagname):-3-len(tagname)]

def grab_json_values(
    llm_output: str
) -> list[dict]:
    return list(extract_json_objects(llm_output))

def compose_multiple_transforms(
    llm_output: str,
    callables: list[callable]
) -> list[dict] | str:
    reformat_output = None
    for reformatter in callables:
        try:
            reformat_output = reformatter(llm_output=llm_output)
            break
        except Exception as ex:
            continue
    if reformat_output is None:
        raise ValueError("Failed reformatting")
    return reformat_output


def cached_generation_and_parsing(
    cache_object: dict,
    cache_path: str,
    cache_key: str,
    wrapped_function: callable,
    parse_function: callable
):
    rawkey = "raw_" + cache_key
    if cache_key in cache_object:
        return_value = cache_object[cache_key]
    else:
        if rawkey in cache_object:
            raw_return_value = cache_object[rawkey]
        else:
            raw_return_value = wrapped_function()
            cache_object[rawkey] = raw_return_value
            save_cache(cache_path, cache_object)
        return_value = parse_function(llm_output=raw_return_value)
        cache_object[cache_key] = return_value
        save_cache(cache_path, cache_object)
    print(cache_object[rawkey])
    print(return_value)
    return return_value
    

def generate_recommendation(
    request_id: str | int,
    user_query: UserQuery,
    opportunities_list: list[GeneralProfile],
    competitor_list: list[CafeProfile]
) -> str:  
    cache_file = os.path.join(CACHE_DIR, f"{request_id}.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            cached_results = json.load(f)
    else:
        cached_results = dict()
    print("Generating opportunity analysis..")
    opportunity_summary = cached_generation_and_parsing(
        cached_results,
        cache_file,
        "opportunity_summary",
        partial(generate_opportunity_analysis, opportunities_list=opportunities_list, user_query=user_query),
        partial(grab_xml_tag, tagname="final_answer")
    )
    print("Generating opportunity analysis DONE.")
    # print(opportunity_summary)
    print("generating competitor swot")
    competitor_swot = cached_generation_and_parsing(
        cached_results,
        cache_file,
        "competitor_swot",
        partial(generate_swot_analysis, subject_list=competitor_list, opportunity_summary=opportunity_summary),
        grab_json_values
    )
    print("generating competitor swot DONE")
    # print(competitor_swot)
    print("generating self SWOT")
    self_swot = cached_generation_and_parsing(
        cached_results,
        cache_file,
        "self_swot",
        partial(generate_swot_analysis, subject_list=[user_query], opportunity_summary=opportunity_summary),
        grab_json_values
    )
    print("generating self SWOT DONE")
    # print(self_swot)
    print("generating gap analysis")
    gap_analysis = cached_generation_and_parsing(
        cached_results,
        cache_file,
        "gap_analysis",
        partial(generate_gap_analysis, self_swot=self_swot, competitor_swot=competitor_swot, opportunity_summary=opportunity_summary),
        partial(grab_xml_tag, tagname="gap_analysis_report")
    )
    print("generating gap analysis DONE")
    # print(gap_analysis)
    print("generating recommendation")
    recommendations = cached_generation_and_parsing(
        cached_results,
        cache_file,
        "recommendation",
        partial(generate_recommendations, gap_analysis=gap_analysis, self_swot=self_swot, competitor_swot=competitor_swot, opportunity_summary=opportunity_summary),
        partial(compose_multiple_transforms, callables=[
            partial(grab_xml_tag, tagname="output"),
            grab_markdown
        ])
    )
    print("generating recommendation DONE")
    return recommendations
    