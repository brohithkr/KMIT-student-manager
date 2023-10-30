from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from ninja import NinjaAPI
from ninja.security import HttpBearer
from passes.models import *
from datetime import datetime, timedelta
from dateutil import relativedelta

import passes.secret_config as secrets

class Auth(HttpBearer):
    def authenticate(self, request, token):
        if token == secrets.auth_token:
            return True
        return False

api = NinjaAPI(auth=Auth())

@api.post("/gen_pass")
def gen_pass(request: HttpRequest, reqPass: ReqPass ):
    today = datetime.now()

    already_issued = IssuedPass.objects.filter(
        roll_no = reqPass.roll_no,
        valid_till__gt= int(today.timestamp())
    )

    if already_issued.count() > 0:
        return HttpResponse(f"Warning: {reqPass.roll_no} already owns a pass")

    valid_till = today
    if reqPass.pass_type == "one_time" :
        valid_till = today + timedelta(days=1)
    if reqPass.pass_type == "daily" :
        valid_till = today + relativedelta(months=6)
    if reqPass.pass_type == "alumni":
        valid_till = today + relativedelta(years=70)
    
    
    IssuedPass.objects.create(
        roll_no=reqPass.roll_no,
        pass_type=reqPass.pass_type,
        issues_date=today.timestamp(),
        valid_till=valid_till.timestamp()
    )
    return "success"


