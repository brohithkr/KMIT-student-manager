import json
from urllib import response

from django.http import HttpResponse, HttpRequest
from ninja import NinjaAPI
from datetime import datetime
from typing import Union
from latecomers.models import *
from server.utlis import Auth
from passes.utlis import get_local_date

api = NinjaAPI(urls_namespace="latecomers")


@api.post("", auth=Auth(), response=Result)
def rem_latecomers(request: HttpRequest):
    body = json.loads(request.body)
    result = Result(success=True, msg="")
    today = datetime.today()
    if type(body) != list:
        try:
            todayCount = Latecomers.objects.filter(roll_no=body["roll_no"], date=body["date"]).count()
            lateCount = Latecomers.objects.filter(roll_no=body["roll_no"]).count()
            if todayCount == 0:
                Latecomers.objects.create(roll_no=body["roll_no"], date=body["date"])
                result.msg = f"Scanned successfully.\nStudent has been late for {lateCount} times earlier."
            else:
                result.msg = f"Roll no has been scanned.\nStudent has been late for {lateCount} times earlier."
        except:
            result.success = False
            result.msg = "Not able to scan. Please try again."
    else:
        for i in body:
            print(i)
            Latecomers.objects.create(roll_no=i["roll_no"], date=i["date"])

    return result


@api.get("")
def latecomers(request, ret_type="json", frm=None, to=None, rollno=None):
    latecomers_qs = Latecomers.objects.all()

    if frm and to:
        from_stamp = datetime.strptime(frm, "%d-%m-%Y").timestamp()
        to_stamp = datetime.strptime(to, "%d-%m-%Y").timestamp()
        latecomers_qs = latecomers_qs.filter(date__range=[from_stamp, to_stamp])

    if rollno:
        latecomers_qs = latecomers_qs.filter(roll_no=rollno)

    if latecomers_qs.count() == 0:
        return HttpResponse("No latecomers found.")

    if ret_type == "json":
        res = [i.json() for i in latecomers_qs]
        return HttpResponse(json.dumps(res), content_type="application/json")
    if ret_type == "csv":
        res = ""
        for i in latecomers_qs:
            if res == "":
                res += str(list(i.json().keys())).strip("[]").replace("'", "") + "\n"
            res += (
                str(list(i.json().values()))
                .strip("[]")
                .replace("'", "")
                .replace(str(i.date), get_local_date(i.date))
                + "\n"
            )
        return HttpResponse(
            res,
            content_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=latecomers_{int(datetime.now().timestamp())}.csv"
            },
        )
