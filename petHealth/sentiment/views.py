from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .classifier import classify_comment

@csrf_exempt
def analyze_comment(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body)
    text = data.get("comment", "").strip()

    if not text:
        return JsonResponse({"error": "Empty comment"}, status=400)

    result = classify_comment(text)

    return JsonResponse({
        "is_spam": result["is_spam"],
        "sentiment": result["sentiment"]
    })
