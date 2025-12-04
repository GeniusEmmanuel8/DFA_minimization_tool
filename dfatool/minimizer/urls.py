from django.urls import path
from .views import minimize_dfa_api

urlpatterns = [
    path("api/minimize-dfa/", minimize_dfa_api, name="minimize_dfa_api"),
]
