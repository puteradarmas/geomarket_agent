from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from sqlalchemy.orm import sessionmaker
from .models import Base, request_hist
from .schemas import request_schema
from sqlalchemy import create_engine


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
            theme = data.get("theme")
            budget = data.get("budget")
            location = data.get("location")
            if location is None:
                location = {"lat": 1.0, "lng": 1.0}  # Default location if not provided
            cafe_list = ['Cafe A', 'Cafe B', 'Cafe C','A la Cafe','La la cafe']  # Example cafe list
            opportunities_list = ['Hospital A','school A','Hospital B','School B','office A']  # Example opportunities list
            num_of_reviews = 200
            avg_review_score = 3.4
            
            print("this much passed")
            
            
            request_data = request_schema(lat=location["lat"], lgn=location["lng"], 
                                        additional_prompt=theme)
            
            
            request_hist_model = request_hist(**request_data.dict())
            print("Request Data:", request_data)
            print("Request Model:", request_hist_model)
            
            # Add and commit to the database
            session.add(request_hist_model)
            session.commit()
            
            request_hist_result = session.query(request_hist).all()

            for reqs in request_hist_result:
                print(f"ID: {reqs.id}, Name: {reqs.lat}, Age: {reqs.lgn}, Created At: {reqs.additional_prompt}, Created At: {reqs.created_at}")

            print("Received:", theme, budget, location,
                  data,type(location['lat']))
            
            Suggestion_1 = "Lorem Ipsum A"
            Suggestion_2 = "Lorem Ipsum B" 
            Suggestion_3 = "Lorem Ipsum C"
            


            # Semangat bikin logika ML
            
            
            return JsonResponse({"status": "Analyze prosessing completed", "message": {"theme": theme, "budget": budget, 
                                                                                       "location": location, "cafe_list": cafe_list, 
                                                                                       "opportunities_list": opportunities_list, 
                                                                                       "num_of_reviews": num_of_reviews, 
                                                                                       "avg_review_score": avg_review_score,
                                                                                       "suggestion1":Suggestion_1,
                                                                                       "suggestion2":Suggestion_2,
                                                                                       "suggestion3":Suggestion_3}}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

