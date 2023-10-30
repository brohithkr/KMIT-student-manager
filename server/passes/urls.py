from django.urls import path
from passes.views import api

urlpatterns = [
    path("", api.urls)
]