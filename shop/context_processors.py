from django.conf import settings
from django.utils import translation
import re

def language_context(request):
    current_path = request.path
    current_lang = translation.get_language()
    if current_lang:
        current_lang = current_lang.split('-')[0]  # Get just the language code without region
    else:
        current_lang = settings.LANGUAGE_CODE.split('-')[0]
    
    # Remove any existing language prefix from the path
    path_without_lang = re.sub(r'^/(fr|en|ar)/', '/', current_path)
    
    languages = []
    for code, name in settings.LANGUAGES:
        languages.append({
            'code': code,
            'name': name,
            'active': code == current_lang,
            'url': f'/{code}{path_without_lang}'
        })
    
    return {
        'available_languages': languages,
        'current_language': current_lang,
        'path_without_lang': path_without_lang,
    }