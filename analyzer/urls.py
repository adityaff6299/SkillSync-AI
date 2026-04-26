from django.urls import path
from . import views

urlpatterns = [
    # 1. The main landing page (The logical choice tree)
    path('', views.home, name='home'),
    
    # 2. The processing URL (Where the form data is sent for matching)
    path('analyze/', views.analyze, name='analyze'),
]