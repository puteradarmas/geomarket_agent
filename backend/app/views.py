from django.http import JsonResponse,FileResponse
from django.views.decorators.csrf import csrf_exempt
import json
from sqlalchemy.orm import sessionmaker
from .models import Base, request_hist
from .schemas import request_schema
from sqlalchemy import create_engine
from .ml_codes.grab_locations import grab_locations_competitor, grab_locations_opportunity
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
            print("Received data:", data)
            
            additional_prompt = data.get("additional_prompt")
            location = data.get("location")
            
            if location is None:
                location = {"lat": -6.200000, "lng": 50.0}  # Default location if not provided

                
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
            
            print("Data saved to database successfully. ID:", request_hist_model.id)

            Suggestion = '''
            The standard Lorem Ipsum passage, used since the 1500s
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."\n
            \n \n
            Section 1.10.32 of "de Finibus Bonorum et Malorum", written by Cicero in 45 BC
            "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?"\n
            \n \n
            1914 translation by H. Rackham
            "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure. To take a trivial example, which of us ever undertakes laborious physical exercise, except to obtain some advantage from it? But who has any right to find fault with a man who chooses to enjoy a pleasure that has no annoying consequences, or one who avoids a pain that produces no resultant pleasure?"\n
            \n \n
            Section 1.10.33 of "de Finibus Bonorum et Malorum", written by Cicero in 45 BC
            "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat."
            ''' 
            


            # Semangat bikin logika ML
            
            
            return JsonResponse({"status": "Analyze prosessing completed", "message": {"additional_prompt": additional_prompt, 
                                                                                       "longitude": location["lng"],"latitude":location["lat"],
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
                    "additional_prompt": req.additional_prompt,
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
    # session = Session()
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
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
            
            return JsonResponse({"status": "Analyze prosessing completed", "message": {"detail_hist":data}}, status=200)   
       
       
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
        

