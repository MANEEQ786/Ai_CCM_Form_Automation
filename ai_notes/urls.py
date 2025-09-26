from django.urls import path
from . import views
from django.conf import settings  # Import settings
from django.conf.urls.static import static 

app_name = 'ai_notes'

urlpatterns = [
    path("home/", views.Home.as_view() , name="Home"),
    path("", views.Test.as_view() , name="test"),
    path('ai_notes/', views.GetAiNotes.as_view(), name='get_ai_notes'),
];
if settings.DEBUG:              
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)