import json
import base64

from django.http import HttpResponse, HttpRequest
from ninja import NinjaAPI
from passes.models import (
    ReqPass,
    IssuedPass,
    ReqLunchTiming,
    ResStudent,
    Result,
    LunchTiming,
    Student
)
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from typing import List
import requests

from passes import utlis
from server.utlis import Auth

api = NinjaAPI()


@api.post("/gen_pass", auth=Auth())
def gen_pass(request: HttpRequest, reqPass: ReqPass):
    today = datetime.now()

    valid_passes = IssuedPass.objects.filter(
        roll_no=reqPass.roll_no, valid_till__gt=int(today.timestamp())
    )

    passCount = valid_passes.filter(pass_type=reqPass.pass_type).count()

    if passCount > 0:
        return HttpResponse(
            f"Warning: {reqPass.roll_no} already owns a {reqPass.pass_type} pass"
        )

    valid_till = today
    if reqPass.pass_type == "one_time":
        valid_till = today + timedelta(days=1)
    if reqPass.pass_type == "daily":
        valid_till = today + relativedelta(months=6)
    if reqPass.pass_type == "alumni":
        valid_till = today + relativedelta(years=70)
    if reqPass.pass_type == "namaaz":
        valid_till = today + timedelta(days=1)

    IssuedPass.objects.create(
        roll_no=reqPass.roll_no,
        pass_type=reqPass.pass_type,
        issues_date=int(today.timestamp()),
        valid_till=int(valid_till.timestamp()),
    )
    return "success"


@api.post("/edit_timings", auth=Auth())
def edit_timings(request: HttpRequest, timings: List[ReqLunchTiming]):
    body: List[dict] = json.loads(request.body)

    timings_lst = [LunchTiming(year=i + 1, **body[i]) for i in range(0, len(body))]
    for i in timings:
        LunchTiming.objects.bulk_update_or_create(  # type: ignore
            timings_lst, ["opening_time", "closing_time"], match_field="year"
        )
    return "success"


@api.get("/get_timings")
def get_timings(request: HttpRequest):
    res = LunchTiming.objects.all()
    res_json = [i.json() for i in res]
    return HttpResponse(json.dumps(res_json), content_type="application/json")


@api.get("/isvalid", auth=Auth(), response={200: Result, 404: Result})
def is_valid(request: HttpRequest, rollno: str):
    result = Result(success=True, msg="")
    today = datetime.today()
    is_valid_rollno = (
        Student.objects.filter(
            rollno=rollno
        ).count() > 0
    )
    if not is_valid_rollno:
        result.success = False
        result.msg = "Invalid rollno"
        return 404, result
    resPass = IssuedPass.objects.filter(
        roll_no=rollno, valid_till__gt=today.timestamp()
    ).last()

    if not resPass:
        result.success = False
        result.msg = "No passes found."
        return 404 ,result

    if resPass.pass_type == "alumni" or resPass.pass_type == "one_time":
        result.msg = f"Roll No. {rollno} has valid pass."
        return result

    timings = utlis.get_timings(
        today.astimezone(pytz.timezone("Asia/Kolkata")),
        utlis.roll_to_year(rollno),
    )

    if resPass.valid_till < int(today.timestamp()):
        result.success = False
        result.msg = "Not valid passes found."
        return result

    if not (
        timings["open"]
        < today.astimezone(pytz.timezone("Asia/Kolkata"))
        < timings["close"]
    ):
        result.success = False
        result.msg = "Not the appropriate time"
        return result

    if resPass.pass_type == "namaaz":
        if today.isoweekday() != 5:
            result.success = False
            result.msg = "Invalid Pass"
            return result

    last_logged_time = utlis.log(roll_no=rollno)
    result.msg = f"Last scanned on {last_logged_time}"
    return result

@api.get("/truncate")
def rmv_passes(
    request: HttpRequest,
    no: str,
):
    allpass = IssuedPass.objects.filter(roll_no = no)
    pass_ = IssuedPass.objects.filter(roll_no = no, pass_type = "one_time")
    if pass_.count() > 0:   
        lst = pass_[pass_.count() - 1]
        if lst.pass_type == 'one_time':
            lst.delete()
        
    res = [i.json() for i in allpass]
    return HttpResponse(json.dumps(res), content_type="application/json")
    

@api.get("/get_issued_passes", description="Lets you download all passes")
def get_issues_passes(
    request: HttpRequest,
    ret_type="json",
    frm=None,
    to=None,
    rollno=None,
):
    # pass_lst = None
    pass_qs = IssuedPass.objects.all()
    if frm and to:
        from_stamp = datetime.strptime(frm, "%d-%m-%Y").timestamp()
        to_stamp = datetime.strptime(to, "%d-%m-%Y").timestamp() + (24 * 60 * 60)
        pass_qs = pass_qs.filter(
            issues_date__range=[from_stamp, to_stamp],
        )

    if rollno:
        pass_qs = pass_qs.filter(roll_no=rollno)

    if len(pass_qs) == 0:
        return HttpResponse("No passes found.")

    if ret_type == "json":
        res = [i.json() for i in pass_qs]
        return HttpResponse(json.dumps(res), content_type="application/json")
    if ret_type == "csv":
        res = ""
        for i in pass_qs:
            if res == "":
                res += str(list(i.json().keys())).strip("[]").replace("'", "") + "\n"
            res += (
                str(list(i.json().values()))
                .strip("[]")
                .replace("'", "")
                .replace(str(i.valid_till), utlis.get_local_date(i.valid_till))
                .replace(str(i.issues_date), utlis.get_local_date(i.issues_date))
                + "\n"
            )
        return HttpResponse(
            res,
            content_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=passes_{int(datetime.now().timestamp())}.csv"
            },
        )


@api.get("/get_valid_passes")
def get_valid_passes(request: HttpRequest):
    today = datetime.today()
    pass_qs = IssuedPass.objects.filter(valid_till__gt=today.timestamp())
    pass_json = [i.json() for i in pass_qs]
    print(pass_json)

    return HttpResponse(json.dumps(pass_json), content_type="application/json")


@api.get("/get_student_data", auth=Auth(), response={200: ResStudent, 404: str})
def get_student_data(request: HttpRequest, rollno: str):
    res = Student.objects.filter(rollno=rollno).first()
    if res == None:
        return 404, "No rollno found"
    picture_bytes = None
    try:
        image_res = requests.get(str(res.picture), timeout=3)
        picture_bytes = image_res.content
        picture_b64 = base64.b64encode(picture_bytes)
        res.picture = picture_b64.decode()
        if image_res.status_code == 403:
            res.picture = None
    except:  # noqa: E722
        res.picture = None

    return 200, res
