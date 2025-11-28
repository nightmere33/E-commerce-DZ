from django.conf import settings
from django.urls import reverse

def language_context(request):
    current_path = request.path
    languages = []
    
    for code, name in settings.LANGUAGES:
        languages.append({
            'code': code,
            'name': name,
            'active': code == request.LANGUAGE_CODE,
            'url': f'/{code}{current_path}' if code != 'fr' else current_path  # French is default
        })
    
    return {
        'available_languages': languages,
        'current_language': request.LANGUAGE_CODE,
    }