from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

# Non-localized URLs
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Localized URLs - these will have language prefix like /en/, /fr/, /ar/
urlpatterns += i18n_patterns(
    path('cart/', include('cart.urls')),
    path('', include('shop.urls')),
    prefix_default_language=True  # This ensures /fr/ is also shown for French
)

# Add this for serving media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)