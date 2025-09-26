from django.urls import path
from . import views
from django.conf import settings  # Import settings
from django.conf.urls.static import static 

app_name = 'ccm_initialfroms'

urlpatterns = [
    # path("home/", views.Home.as_view() , name="Home"),
    path("", views.Test.as_view() , name="test"),
    path("get_initial_forms/", views.GetInitForms.as_view() , name="Encounter"),
    path("get_logs/", views.GetLogs.as_view() , name="Logs"),
];
if settings.DEBUG:              
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)