from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .chroma_service import ChromaService

@csrf_exempt
@require_http_methods(["POST"])
def add_documents(request):
    try:
        data = json.loads(request.body)
        ids = data["ids"]
        documents = data["documents"]
        metadatas = data["metadatas"]
        ChromaService.add_documents(ids, documents, metadatas)
        return JsonResponse({"message": "Documents added successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
