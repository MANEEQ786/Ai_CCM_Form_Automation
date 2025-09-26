from django.urls import path
from . import views
from django.conf import settings  # Import settings
from django.conf.urls.static import static 

app_name = 'ccm_followUp_forms'

urlpatterns = [
    path("home/", views.Home.as_view() , name="Home"),
    path("", views.Test.as_view() , name="test"),
    path("get_followup_form/", views.GetFollowUpForm.as_view() , name="FollowUp"),
    path("get_chronic_icds/", views.Predict_icd.as_view() , name="icd"),
];
if settings.DEBUG:              
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)