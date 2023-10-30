from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.core import serializers
from ninja import NinjaAPI
from ninja.security import HttpBearer
from passes.models import *
from datetime import datetime, timedelta
import time
from dateutil import relativedelta
import pytz
from typing import List
import passes.secret_config as secrets
from passes import utlis


class Auth(HttpBearer):
    def authenticate(self, request, token):
        if token == secrets.auth_token:
            return True
        return False


api = NinjaAPI()


@api.post("/gen_pass", auth=Auth())
def gen_pass(request: HttpRequest, reqPass: ReqPass):
    today = datetime.now()

    already_issued = IssuedPass.objects.filter(
        roll_no=reqPass.roll_no, valid_till__gt=int(today.timestamp())
    )

    if already_issued.count() > 0:
        return HttpResponse(f"Warning: {reqPass.roll_no} already owns a pass")

    valid_till = today
    if reqPass.pass_type == "one_time":
        valid_till = today + timedelta(days=1)
    if reqPass.pass_type == "daily":
        valid_till = today + relativedelta(months=6)
    if reqPass.pass_type == "alumni":
        valid_till = today + relativedelta(years=70)

    IssuedPass.objects.create(
        roll_no=reqPass.roll_no,
        pass_type=reqPass.pass_type,
        issues_date=today.timestamp(),
        valid_till=valid_till.timestamp(),
    )
    return "success"


@api.post("/edit_timings", auth=Auth())
def edit_timings(request: HttpRequest, timings: List[ReqLunchTiming]):
    year = 1
    for i in timings:
        LunchTiming.objects.update_or_create(
            year=year, opening_time=i.opening_time, closing_time=i.closing_time
        )
        year += 1
    return "success"


@api.get("/isvalid", )
def get_latest_valid_pass(request: HttpRequest, rollno: str):
    result = Result(success=True, msg="")
    today = datetime.today()
    resPass = IssuedPass.objects.filter(
        roll_no=rollno, valid_till__gt=today.timestamp()
    ).get()

    timings = utlis.get_timings(
            today.astimezone(pytz.timezone("Asia/Kolkata")), utlis.roll_to_year(rollno)
        )
    
    if resPass.pass_type == "alumni":
        return resPass
    
    if resPass.valid_till < int(today.timestamp):
        result.success = False
        result.msg = "No valid passes found."
        return result
    if not (
        today > timings["open"]
        and today < timings["close"]
    ):
        result.success = False
        result.msg = "Not the time"
    


@api.get("/get_issued_passes")
def get_issues_passes(request: HttpRequest, ret_type, frm, to, rollno ):
    pass_lst = None
    if frm!=None and to!=None :
        pass_qs = IssuedPass.objects.filter(
            
        )
