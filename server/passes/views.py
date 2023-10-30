from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from ninja import NinjaAPI
from ninja.security import HttpBearer
from passes.models import *
from datetime import datetime
from dateutil import relativedelta
class Auth(HttpBearer):
    def authenticate(self, request, token):
        if token == "hello":
            return True
        return False

api = NinjaAPI(auth=Auth())

@api.post("/gen_pass")
def gen_pass(request: HttpRequest, reqPass: ReqPass ):

    today = datetime.now()

    already_issued = IssuedPass.objects.filter(
        roll_no = reqPass.roll_no,
        valid_till__greater_than = int(today.timestamp())
    )

    if already_issued.count > 0:
        return HttpResponse(f"Warning: {reqPass.roll_no} already owns a pass")
    
    if reqPass.pass_type == "one_time" :
        valid_till = today.timestamp + (24*60*60)
    if reqPass.pass_type == "daily" :
        valid_till = today + relativedelta(months=6)
    if reqPass.pass_type == "alumni":
        valid_till = today + relativedelta(years=70)
    
    # IssuedPass.objects.create(
    #     roll_no = 
    # )




    pass

