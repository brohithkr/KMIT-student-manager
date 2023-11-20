from django.urls import path
from latecomers.views import api

urlpatterns = [
    path("", api.urls)
]