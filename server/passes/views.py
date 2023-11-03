import json

from django.http import HttpResponse, HttpRequest
from ninja import NinjaAPI
from passes.models import *
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from typing import List

from passes import utlis
from server.utlis import Auth

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
    body: List[dict] = json.loads(request.body)

    timings_lst = [LunchTiming(year=i + 1, **body[i]) for i in range(0, len(body))]
    for i in timings:
        LunchTiming.objects.bulk_update_or_create(
            timings_lst, ["opening_time", "closing_time"], match_field="year"
        )
    return "success"


@api.get("/isvalid")
def is_valid(request: HttpRequest, rollno: str):
    result = Result(success=True, msg="")
    today = datetime.today()
    resPass = IssuedPass.objects.filter(
        roll_no=rollno, valid_till__gt=today.timestamp()
    ).last()

    if not resPass:
        result.success = False
        result.msg = "No passes found."
        return result

    timings = utlis.get_timings(
        today.astimezone(pytz.timezone("Asia/Kolkata")),
        utlis.roll_to_year(rollno),
    )

    if resPass.pass_type == "alumni":
        return resPass

    if resPass.valid_till < int(today.timestamp()):
        result.success = False
        result.msg = "No valid passes found."
        return result
    if not (
        timings["open"]
        < today.astimezone(pytz.timezone("Asia/Kolkata"))
        < timings["close"]
    ):
        result.success = False
        result.msg = "Not the time"
        return result
    return result


@api.get("/get_issued_passes", description="Lets you download all passes")
def get_issues_passes(
    request: HttpRequest,
    ret_type=None,
    frm=None,
    to=None,
    rollno=None,
):
    pass_lst = None
    pass_qs = IssuedPass.objects.all()
    if frm and to:
        from_stamp = datetime.strptime(frm, "%d-%m-%Y").timestamp()
        to_stamp = datetime.strptime(to, "%d-%m-%Y").timestamp() + (24 * 60 * 60)
        # print(pass_qs.values())
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
