from detailpetcare.models import DetailPetcare

def detail_petcare(request):
    try:
        detail = DetailPetcare.objects.first()
    except Exception:
        detail = None
    return {'detail_petcare': detail}
  
def current_route(request):
    match = request.resolver_match
    return {
        'namespace': match.namespace if match else '',
        'url_name': match.url_name if match else ''
    }
