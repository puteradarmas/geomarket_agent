import json
from sqlalchemy.orm import sessionmaker
from .models import Base, request_hist
from .schemas import request_schema
from sqlalchemy import create_engine
from .ml_codes.grab_locations import grab_locations_competitor, grab_locations_opportunity,grab_address
from markdown_pdf import MarkdownPdf,Section
import os
from hashlib import sha256

from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .ml_codes.grab_locations import (
    grab_address,
    grab_locations_competitor,
    grab_locations_opportunity,
)
# from .ml_codes.processors.place_processor import process_opportunity, process_place
# from .ml_codes.recommendation import generate_recommendation
# from .ml_codes.schemas import CafeProfile, GeneralProfile, UserQuery
from .models import request_hist
from .schemas import request_schema

PROFILES_CACHE_PATH = "outputs/profiles/"


@csrf_exempt  # only for development, use proper CSRF in production
def analyze_data(request):
    engine = create_engine("sqlite:///db.sqlite3", echo=True)

    # Base.metadata.drop_all(bind=engine)  # Careful: deletes data
    # Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            additional_prompt = data.get("additional_prompt")
            location = data.get("location")
            if location is None:
                location = {
                    "lat": -6.200000,
                    "lng": 106.816666,
                }  # Default location if not provided

            address = grab_address(location) # Get address from lat/lng

            json_locations_competitor = grab_locations_competitor(
                location["lat"], location["lng"]
            )["places"]  # Get nearby cafes
            json_locations_opportunities = grab_locations_opportunity(
                location["lat"], location["lng"]
            )["places"]  # Get nearby opportunities

            # # Process the opportunities
            # processed_opportunities: list[GeneralProfile] = [
            #     process_opportunity(opp) for opp in json_locations_opportunities
            # ]

            # processed_competitors: list[CafeProfile] = []

            # # Process the competitors
            # for competitor in json_locations_competitor:
            #     place_id = competitor["id"]
            #     fullpath = os.path.join(PROFILES_CACHE_PATH, f"{place_id}.json") # Cache path for competitors profiles
            #     if os.path.exists(fullpath):
            #         with open(fullpath, "r") as f:
            #             cafe_profile = CafeProfile.model_validate_json(f.read())
            #     else:
            #         cafe_profile = process_place(competitor)
            #     processed_competitors.append(cafe_profile)
            # request_id = sha256(
            #     f"{additional_prompt}-{location['lat']}-{location['lng']}"
            # ).hexdigest()
            # recommendation = generate_recommendation(   # Generate recommendation
            #     request_id=request_id,
            #     user_query=UserQuery(
            #         description=additional_prompt,
            #         latlong=[location["lat"], location["lng"]],
            #     ),
            #     opportunities_list=processed_opportunities,
            #     competitor_list=processed_competitors,
            # )
            recommendation = "This is a sample recommendation based on the provided data. Please implement the actual recommendation logic."
            
            # create pydantic schema instance
            request_data = request_schema(
                lat=location["lat"],
                lgn=location["lng"],
                address=address,
                additional_prompts=additional_prompt,
                reccommendation_result=recommendation,
            )

            # from pydantic schema, create SQLAlchemy model instance
            request_hist_model = request_hist(**request_data.dict())
            markdown_file = "outputs\recommendations\MONAS.md"
            
            # Add and commit to the database
            session.add(request_hist_model)
            session.commit()

            print("Data saved to database successfully. ID:", request_hist_model.id)
            
            
            ## Genereate PDF from recommendation
            pdf = MarkdownPdf(toc_level=2, optimize=True)         
            pdf.add_section(Section(recommendation),user_css="table, th, td {border: 1px solid black;}")          
            pdf.save(r"C:/Users/puter/Documents/git/geomarket_agent_research/geomarket_agent/outputs/recommendations/reccommendation_output_"+str(request_hist_model.id)+".pdf")

            # Semangat bikin logika ML

            return JsonResponse(
                {
                    "status": "Analyze prosessing completed",
                    "message": {
                        "request_id": request_hist_model.id,
                        "additional_prompt": additional_prompt,
                        "longitude": location["lng"],
                        "latitude": location["lat"],
                        "address": address,
                        "suggestion": recommendation,
                    },
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt  # only for development, use proper CSRF in production
def get_history(request):
    engine = create_engine("sqlite:///db.sqlite3", echo=True)

    # Base.metadata.drop_all(bind=engine)  # Careful: deletes data
    # Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    if request.method == "GET":
        try:
            request_hist_result = session.query(request_hist).all()

            hist_data = []
            for req in request_hist_result:
                hist_data.append(
                    {
                        "id": req.id,
                        "lat": req.lat,
                        "lgn": req.lgn,
                        "address": req.address,
                        "created_at": str(req.created_at),  # Convert datetime to string
                    }
                )

            return JsonResponse(
                {
                    "status": "Analyze prosessing completed",
                    "message": {"hist_data": hist_data},
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# @csrf_exempt  # only for development, use proper CSRF in production
# def download_file(request):


@csrf_exempt  # only for development, use proper CSRF in production
def view_history(request):
    engine = create_engine("sqlite:///db.sqlite3", echo=True)

    Session = sessionmaker(bind=engine)
    session = Session()

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Data received:", data)
            hist_id = data.get("id")
            print("Request ID:", hist_id)

            req_hist_data = session.query(request_hist).filter_by(id=hist_id).first()

            location = {"lat": req_hist_data.lat, "lng": req_hist_data.lgn}
            address = req_hist_data.address
            additional_prompt = req_hist_data.additional_prompts
            Suggestion = req_hist_data.reccommendation_result
            
            # result_file_path = r"C:\Users\puter\Documents\git\geomarket_agent_research\geomarket_agent\outputs\recommendations"
            
            with open(r"C:/Users/puter/Documents/git/geomarket_agent_research/geomarket_agent/outputs/recommendations/MONAS.md", "r", encoding="utf-8") as f:
                md_text = f.read()
            
            return JsonResponse({"status": "Analyze prosessing completed", "message": {"request_id":hist_id,
                                                                                       "additional_prompt": additional_prompt, 
                                                                                       "longitude": location["lng"],"latitude":location["lat"],
                                                                                       "address": address,
                                                                                       "suggestion":md_text}}, status=200)
       
       
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
