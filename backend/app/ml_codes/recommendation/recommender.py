import re
import json
import os
from jinja2 import Template
from app.ml_codes.schemas import GeneralProfile, CafeProfile, UserQuery
from app.ml_codes.recommendation.opportunity import generate_opportunity_analysis
from functools import partial
from app.ml_codes.recommendation.swot import generate_swot_analysis

from app.ml_codes.processors.place_processor import persist_cache, extract_json_objects

from app.ml_codes.agents import gemini_agent
from app.ml_codes.schemas import ReasoningAndOutput

from typing import TypeVar, Callable

ParsedOutputType = TypeVar("ParsedOutputType")
ModelOutputType = TypeVar("ModelOutputType")

CACHE_DIR = "outputs/recommender_intermediate"
os.makedirs(CACHE_DIR, exist_ok=True)

GAP_ANALYSIS_PROMPT_TEMPLATE = Template("""\
# Role
You are a senior business analyst specializing in retail and F&B gap analyses. Conduct a professional gap analysis for a cafe business using ONLY user-provided data. Never invent facts or make assumptions.

# Instruction
Follow the provided analysis framework and adhere to the output format provided below.
First, think and reason about each steps of your detailed analysis. Put your reasoning in a separate `reasoning` section.
Afterwards, generate your final answer following the output format in the `output` section.

# Background Context
The user is establishing/optimizing a cafe in a competitive area nearby cafes. You will receive:
1. Demographic analysis of the immediate area provided in `demographic_analysis`
2. SWOT analysis of the user's cafe concept, provided in `user_swot`
3. SWOTs analysis of competitor cafes, provide in `competitor_cafe_swots`

# Rules
- Strictly use only provided data - never invent or extrapolate
- State "Insufficient data: [missing element]" if inputs are incomplete
- Quantify comparisons using relative terms (e.g., "20% higher pricing")
- Prioritize actionable opportunities with clear exploitation paths
- Maintain neutral objectivity when analyzing all SWOTs

# Analysis Framework
1. UNMET NEEDS: Identify demographic needs unaddressed by ANY cafe (including user's), supported by demographic data
2. POSITIONING: Compare user's concept vs competitors by comparing SWOTs strengths/weaknesses
3. VULNERABILITIES: Extract confirmed weaknesses from competitor SWOTs provided in `competitor_cafe_swots` and map to user's strengths provided in `user_swot`
4. FIT GAPS: Evaluate alignment between ALL cafes and demographic data

# Output Format
```markdown
# 1. Unmet Demographic Needs
## Identified Gaps
- [Specific need] (Evidence: [Demographic data reference])
- [Specific need] (Evidence: [Demographic data reference])

## Competitor Coverage Gap
[Summary statement]

# 2. Concept Positioning
## Strengths
[Advantage vs competitors] (Source: [User SWOT Strength])

## Weaknesses
[Disadvantage vs competitors] (Source: [User SWOT Weakness])

## Differentiation Score
[High/Medium/Low] based on uniqueness

# 3. Competitor Vulnerabilities
| Competitor | Weakness | Opportunity |
|------------|----------|-------------|
| [Competitor 1] | [Specific weakness] | [Matching user strength] |
| [Competitor 2] | [Specific weakness] | [Matching user strength] |
| [Competitor N] | [Specific weakness] | [Matching user strength] |

# 4. Demographic Fit Gaps
## User's Cafe Fit
**Alignment:** [Aspect matching demographics]

**Misalignment:** [Aspect conflicting demographics] (Source: [Data reference])

## Competitor Fit Summary
### [Competitor 1]
- **Pricing Misalignment:** [Description]
- **Experience Gaps:** [Description]
- **Service Limitations:** [Description]

### [Competitor 2]
- **Pricing Misalignment:** [Description]
- **Experience Gaps:** [Description]
- **Service Limitations:** [Description]

### [Competitor N]
- **Pricing Misalignment:** [Description]
- **Experience Gaps:** [Description]
- **Service Limitations:** [Description]

## Critical Gaps
[Shared weaknesses across all cafes]

# 5. Strategic Recommendations
## Priority Opportunities
1. [Actionable opportunity] (Targets: [Specific gap/weakness])
2. [Actionable opportunity] (Targets: [Specific gap/weakness])
N. [Actionable opportunity] (Targets: [Specific gap/weakness])

## Concept Adjustments
[Data-backed operational changes]

## Risk Mitigation
[Critical user weaknesses to address]
```

# User Inputs

## Demographic Analysis
{{demographic_analysis}}

## User SWOT
{{user_swot}}

## Competitor Cafe SWOTs
{{competitor_swot}}
""")

RECOMMENDATION_GENERATION_PROMPT_TEMPLATE = Template("""\
# Business Analyst - Cafe Recommendation Report

# Role
You are a professional business analyst. Having done your research, you are here to compile a final recommendation report.

# Background
You are handling a client's request. Given a location and their concept / idea for a cafe, you were tasked to gather information to ultimately compile an analysis of recommendations for the client.

Previously you have made several analysis of the cafe. These will be your input to make the recommendation report:
1. A demographics / opportunity analysis from analyzing the types of locations around a cafe location.
2. A gap analysis of how much the client's cafe fit the opportunity analysis, compared to its nearby competitors (other cafes). This gap analysis has already indirectly integrated the competitor's informations from making comparison.
3. A SWOT analysis of the client's cafe concept made against the opportunity analysis.

# Instruction
Compile the informations provided to create a recommendation report.
Follow the provided format to generate your report.
First reason about each segments of the report, identify and analyze the relevant inputs to generate the analysis for each section. Put your reasoning in a separate `reasoning` section.
After you finished reasoning and feels satisfied, generate the report as your final answer, in the `output` section.
Your output must be markdown-formatted following the format and layout of the given output format.

# Rules
- The report must follow the above structure without any additions.
- Making up facts is unhelpful and harmful.
- Making up another format is also unhelpful and harmful.

# Output Format
```markdown
# Cafe Opportunity Analysis: [cafe name if provided]

## 1. Demographic Opportunity Snapshot
### Summary of target demographics
the summary of the target demographic
### Concept and theme
explanation of the planned concept and theme
### Important considerations
#### Fullfillment methods
explanation of what and why to consider for fullfillment 
#### Facilities and other experience enhancers
explanation of what and why to consider for facilities, besides the one already mentioned 
#### Operating factors
explanation of what and why to consider for other operating factors of the cafe, for example opening hours 
#### Pricing level
explanation of the suggested pricing level and why

## 2. Competitive Landscape
### Market gap analysis from the POV of the client's cafe
your analysis on what the client might lack to enhance the competitiveness of their cafe (with respect to the demographic) but still keeping its concept and character
### Competitor vulnerability map
based on the competitor swots, list and identify important points that might be key to gain competitiveness against surrounding cafe
### Positioning of the client's concept
The SWOT analysis of the client's concept based on the surrounding demographic

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
```

# Inputs
## Demographics Opportunity Analysis
Below is the opportunity analysis based on the inferred demography of the area:
{{ demographics_opportunity_analysis }}

## Gap Analysis
Below is the gap analysis done by comparing the SWOTs analysis of each cafes with each other. The SWOT is analyzed based on how each cafe fares against the opportunity analyzed above.
{{ gap_analysis }}

## Client SWOT
The SWOT of the client cafe:
{{ client_swot }}

## Client Competitors SWOTs
The SWOTs of all of the competing cafes:
{{ competitor_swot }}
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
        full_prompt,
        output_type=ReasoningAndOutput
    ).output
    return gap_analysis_output.output

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
        full_prompt,
        output_type=ReasoningAndOutput
    ).output
    
    return recommendation_output.output

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
    wrapped_function: Callable[..., ModelOutputType],
    parse_function: Callable[[ModelOutputType,], ParsedOutputType]
) :
    rawkey = "raw_" + cache_key
    if cache_key in cache_object:
        return_value = cache_object[cache_key]
    else:
        if rawkey in cache_object:
            raw_return_value = cache_object[rawkey]
        else:
            raw_return_value = wrapped_function()
            cache_object[rawkey] = raw_return_value
            persist_cache(cache_path, cache_object)
        return_value = parse_function(llm_output=raw_return_value)
        cache_object[cache_key] = return_value
        persist_cache(cache_path, cache_object)
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
        lambda x: x
    )
    print("Generating opportunity analysis DONE.")
    print("generating competitor swot")
    competitor_swot = cached_generation_and_parsing(
        cached_results,
        cache_file,
        "competitor_swot",
        partial(generate_swot_analysis, subject_list=competitor_list, opportunity_summary=opportunity_summary),
        lambda x: x
    )
    print("generating competitor swot DONE")
    print("generating self SWOT")
    self_swot = cached_generation_and_parsing(
        cached_results,
        cache_file,
        "self_swot",
        partial(generate_swot_analysis, subject_list=[user_query], opportunity_summary=opportunity_summary),
        lambda x: x
    )
    print("generating self SWOT DONE")
    print("generating gap analysis")
    gap_analysis: str = cached_generation_and_parsing(
        cached_results,
        cache_file,
        "gap_analysis",
        partial(generate_gap_analysis, self_swot=self_swot, competitor_swot=competitor_swot, opportunity_summary=opportunity_summary),
        lambda x: x
    )
    print("generating gap analysis DONE")
    print("generating recommendation")
    recommendations = cached_generation_and_parsing(
        cached_results,
        cache_file,
        "recommendation",
        partial(generate_recommendations, gap_analysis=gap_analysis, self_swot=self_swot, competitor_swot=competitor_swot, opportunity_summary=opportunity_summary),
        lambda x: x
    )
    print("generating recommendation DONE")
    return recommendations
    