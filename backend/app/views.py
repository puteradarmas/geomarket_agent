from django.http import JsonResponse,FileResponse
from django.views.decorators.csrf import csrf_exempt
import json
from sqlalchemy.orm import sessionmaker
from .models import Base, request_hist
from .schemas import request_schema
from sqlalchemy import create_engine
from .ml_codes.grab_locations import grab_locations_competitor, grab_locations_opportunity,grab_address
from .ml_codes.final_recommendation import run_recommendation
import os


@csrf_exempt  # only for development, use proper CSRF in production
def analyze_data(request):
    
    engine = create_engine("sqlite:///db.sqlite3", echo=True)
    
    # Base.metadata.drop_all(bind=engine)  # Careful: deletes data
    # Base.metadata.create_all(bind=engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            additional_prompt = data.get("additional_prompt")
            location = data.get("location")
            if location is None:
                location = {"lat": -6.200000, "lng": 106.816666}  # Default location if not provided
                
            address = grab_address(location)
                
            json_locations_competitor = grab_locations_competitor(location["lat"], location["lng"]) # Get nearby cafes
            json_locations_opportunities = grab_locations_opportunity(location["lat"], location["lng"]) # Get nearby opportunities
            
            ## Add processing review dan gambar here hingga menjadi parameterized, menggunakan json_locations
            
            ## Jalanan generate summary, jangan lupa label kalau dia opportunity atau competitor
            
            ## Generate opportunity dan competitor summary
            
            ## Generate recommendation via Gemini 2.0-flash
            
            final_recommendation_prompt = run_recommendation('prompt')
            
            
            cafe_list = ['Cafe A', 'Cafe B', 'Cafe C','A la Cafe','La la cafe']  # Example cafe list
            opportunities_list = ['Hospital A','school A','Hospital B','School B','office A']  # Example opportunities list
            num_of_reviews = 200
            avg_review_score = 3.4
            
            

            Suggestion = """# Analysis Report
## Key Stats
- Population: **12,345**
- Growth Rate: *2.3%*
## Recommendation
We recommend focusing on the **northern zone** due to higher population density. Tapi bagaimana kalo in panjang spertinya bisa akan menjadi maslah iya ga?"""
            
            # create pydantic schema instance
            request_data = request_schema(lat=location["lat"], lgn=location["lng"], 
                                        address=address,additional_prompts=additional_prompt,reccommendation_result=Suggestion)
            
            # from pydantic schema, create SQLAlchemy model instance
            request_hist_model = request_hist(**request_data.dict())
            print("Request Data:", request_data)
            print("Request Model:", request_hist_model)
            
            # Add and commit to the database
            session.add(request_hist_model)
            session.commit()
            
            print("Data saved to database successfully. ID:", request_hist_model.id)

            # Semangat bikin logika ML
            
            
            return JsonResponse({"status": "Analyze prosessing completed", "message": {"additional_prompt": additional_prompt, 
                                                                                       "longitude": location["lng"],"latitude":location["lat"],
                                                                                       "address": address,
                                                                                       "cafe_list": cafe_list, 
                                                                                       "opportunities_list": opportunities_list, 
                                                                                       "num_of_reviews": num_of_reviews, 
                                                                                       "avg_review_score": avg_review_score,
                                                                                       "suggestion":Suggestion}}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt  # only for development, use proper CSRF in production
def get_history(request):
    
    engine = create_engine("sqlite:///db.sqlite3", echo=True)
    
    # Base.metadata.drop_all(bind=engine)  # Careful: deletes data
    # Base.metadata.create_all(bind=engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    if request.method == 'GET':
        try:
            request_hist_result = session.query(request_hist).all()

            hist_data = []
            for req in request_hist_result:
                hist_data.append({
                    "id": req.id,
                    "lat": req.lat,
                    "lgn": req.lgn,
                    "address": req.address,
                    "created_at": str(req.created_at)  # Convert datetime to string
                })
            
            return JsonResponse({"status": "Analyze prosessing completed", "message": {"hist_data":hist_data}}, status=200)   
       
       
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)        
        
# @csrf_exempt  # only for development, use proper CSRF in production
# def download_file(request):

@csrf_exempt  # only for development, use proper CSRF in production
def view_history(request):
    engine = create_engine("sqlite:///db.sqlite3", echo=True)

    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    if request.method == 'POST':
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
            
            
            
            # request_hist_result = session.query(request_hist).all()

            # hist_data = []
            # for req in request_hist_result:
            #     hist_data.append({
            #         "id": req.id,
            #         "lat": req.lat,
            #         "lgn": req.lgn,
            #         "additional_prompt": req.additional_prompt,
            #         "created_at": str(req.created_at)  # Convert datetime to string
                # })
            
            return JsonResponse({"status": "Analyze prosessing completed", "message": {"additional_prompt": additional_prompt, 
                                                                                       "longitude": location["lng"],"latitude":location["lat"],
                                                                                       "address": address,
                                                                                       "suggestion":Suggestion}}, status=200)
       
       
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
        

