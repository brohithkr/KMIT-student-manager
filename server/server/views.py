from django.http import HttpResponse, HttpRequest
from ninja import NinjaAPI
from passes.models import init_students


def home(request: HttpRequest, initdb=False):
    print(request.method)
    if initdb:
        init_students()
    return HttpResponse("hello world")
