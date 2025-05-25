from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # only for development, use proper CSRF in production
def analyze_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            theme = data.get("theme")
            budget = data.get("budget")
            location = data.get("location")

            print("Received:", theme, budget, location)

            # Do your analysis or machine learning here...

            return JsonResponse({"status": "success", "message": "Analysis complete"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

