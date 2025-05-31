from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from sqlalchemy.orm import sessionmaker
from .models import Base, request_hist
from .schemas import request_schema
from sqlalchemy import create_engine
from .ml_codes.grab_locations import grab_locations_competitor, grab_locations_opportunity
from .ml_codes.final_recommendation import run_recommendation


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
            budget = data.get("budget")
            location = data.get("location")
            if location is None:
                location = {"lat": -50.0, "lng": 50.0}  # Default location if not provided
                
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
            
            
            
            print("this much passed")
            
            # create pydantic schema instance
            request_data = request_schema(lat=location["lat"], lgn=location["lng"], 
                                        additional_prompt=additional_prompt)
            
            # from pydantic schema, create SQLAlchemy model instance
            request_hist_model = request_hist(**request_data.dict())
            print("Request Data:", request_data)
            print("Request Model:", request_hist_model)
            
            # Add and commit to the database
            session.add(request_hist_model)
            session.commit()
            
            print("Data saved to database successfully.")

            Suggestion_1 = "Lorem Ipsum A"
            Suggestion_2 = "Lorem Ipsum B" 
            Suggestion_3 = "Lorem Ipsum C"
            


            # Semangat bikin logika ML
            
            
            return JsonResponse({"status": "Analyze prosessing completed", "message": {"additional_prompt": additional_prompt, "budget": budget, 
                                                                                       "longitude": location["lng"],"latitude":location["lat"],
                                                                                       "cafe_list": cafe_list, 
                                                                                       "opportunities_list": opportunities_list, 
                                                                                       "num_of_reviews": num_of_reviews, 
                                                                                       "avg_review_score": avg_review_score,
                                                                                       "suggestion1":Suggestion_1,
                                                                                       "suggestion2":Suggestion_2,
                                                                                       "suggestion3":Suggestion_3}}, status=200)
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

            id_list = [req.id for req in request_hist_result]
            lat_list = [req.lat for req in request_hist_result]
            lgn_list = [req.lgn for req in request_hist_result]
            additional_prompt_list = [req.additional_prompt for req in request_hist_result]
            created_at_list = [req.created_at for req in request_hist_result]
            
            return JsonResponse({"status": "Analyze prosessing completed", "message": {"id_list": id_list, "lat_list": lat_list, 
                                                                                       "lgn_list":lgn_list,
                                                                                       "additional_prompt_list":additional_prompt_list,
                                                                                       "created_at_list":created_at_list}}, status=200)   
       
       
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)        
        

