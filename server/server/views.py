from django.http import HttpResponse, HttpRequest
from ninja import NinjaAPI
from passes.models import init_students


def home(request: HttpRequest, initdb: bool=False):
    print(request.method)
    print(initdb)
    if initdb:
        init_students()
        return HttpResponse("DB Initialized")
    return HttpResponse("hello world")

def initDB(request: HttpRequest):
    init_students()
    return HttpResponse("DB Initialized")