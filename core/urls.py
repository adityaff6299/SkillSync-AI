from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This connects the main domain to your analyzer app
    path('', include('analyzer.urls')), 
]

# This part is essential for handling resume uploads during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_address=settings.MEDIA_ROOT)