import google.generativeai as genai
import os

# Set your API key

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