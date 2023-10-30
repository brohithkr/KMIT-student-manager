from django.http import HttpResponse, HttpRequest
from ninja import NinjaAPI


def home(request: HttpRequest):
    print(request.method)
    return HttpResponse("hello world")