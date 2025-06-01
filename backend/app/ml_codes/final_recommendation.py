import google.generativeai as genai
import os

# Set your API key

NUANCE_PROMPT = '''You are a professional Market & Location Analyst, There are five places around the area with respective description as below:
1. {OPORTUNITY_1},
2. {OPORTUNITY_2},
3. {OPORTUNITY_3},
4. {OPORTUNITY_4},
5. {OPORTUNITY_5}

Analyze those opportunity to determine the:
1. Opening hour,
2. Price range,
3. Target market,
4. ambiance and amneties,
5. Menu preference

of an ideal/prospective cafe for that area. 
'''

COMPETITOR_SWOT_PROMPT = '''Based on the summary of an ideal cafe from before, which includes factors such as target market, pricing, atmosphere, locations, and opening hour. conduct a SWOT analysis for the following five cafés: 

1. [Cafe A], 
2. [Cafe B], 
3. [Cafe C], 
4. [Cafe D], 
5. Cafe E].

For each cafe, analyze the following:
	•	Strengths: What advantages does this café have in relation to the ideal profile? Consider factors like brand image, customer loyalty, location, unique offerings, or ambiance.
	•	Weaknesses: Where does the café fall short compared to the ideal expectations in the area? Look at pricing, menu limitations, service quality, or visibility.
	•	Opportunities: What trends or local factors can the café take advantage of? Consider emerging consumer preferences, nearby developments, or gaps in the competition.
	•	Threats: What external challenges could impact this cafe’s success in matching the ideal profile? Include strong competitors, rising costs, or changing local demographics.

Use the ideal cafe summary as a benchmark to evaluate how well each cafe aligns with market expectations, and identify areas for improvement or growth.
'''

COMPARATIVE_PROMPT = '''Perform a comparative analysis between a hypothetical café concept and five existing competitor cafés in [insert area name]. The comparison should evaluate each café (including the hypothetical one) based on the following key criteria:
	1.	Opening Hours – Are the hours aligned with the local customer flow and habits? Which cafés open earlier or close later?
	2.	Price Range – How do their prices compare for similar offerings (e.g., coffee, snacks, meals)? Identify affordability and perceived value.
	3.	Location – Analyze the strategic position of each café in relation to foot traffic, accessibility, parking, and nearby attractions or institutions.
	4.	Amenities – Compare facilities such as Wi-Fi, charging ports, seating capacity, outdoor seating, air conditioning, music, quiet/study zones, etc.
	5.	Target Market – Identify the primary customer base each café seems to attract (e.g., students, remote workers, office staff, families, tourists), and how that aligns with the demographic demand in the area.

Use this analysis to:
	•	Highlight the competitive advantages and disadvantages of the hypothetical café.
	•	Identify positioning gaps or opportunities in the market.
	•	Suggest how the hypothetical café could better meet local needs compared to its competitors.'''

def run_recommendation(Prompt):
    """
    Function to run the recommendation model with the provided prompt.
    
    Args:
    Prompt (str): The input prompt for the model.
    
    Returns:
    str: The generated response from the model.
    """
    # Ensure the API key is set
    # if 'GOOGLE_API_KEY' not in os.environ:
    #     raise ValueError("API key is not set. Please set the GOOGLE_API_KEY environment variable.")
    
    # Configure the Generative AI client
    genai.configure(api_key="AIzaSyCeSFDojYhLttdSUP2wgFkjiTHqrNptXfQ")

    # Initialize the model
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Generate a response
    response = model.generate_content(Prompt)
    
    return response.text