from django.shortcuts import render
from django.http import HttpResponse
from ninja import NinjaAPI

api = NinjaAPI()

api.get("/gen_pass")
def gen_pass():




