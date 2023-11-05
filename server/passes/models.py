from django.db import models
from typing import Generic, TypeVar, Union
from bulk_update_or_create import BulkUpdateOrCreateQuerySet
import json


class IssuedPass(models.Model):
    PASS_TYPES = [("one_time", "one_time"), ("daily", "daily"), ("alumni", "alumni")]
    roll_no = models.CharField(max_length=11)
    issues_date = models.BigIntegerField("Unix time stamp of issued date.")
    valid_till = models.BigIntegerField("Unix time stamp of expiry date.")
    pass_type = models.CharField(max_length=10)

    def json(self):
        return {
            "roll_no": self.roll_no,
            "issue_date": self.issues_date,
            "valid_till": self.valid_till,
            "pass_type": self.pass_type,
        }

    class Meta:
        db_table = "issued_pass"


class LunchTiming(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    year = models.IntegerField()
    opening_time = models.CharField(max_length=10)
    closing_time = models.CharField(max_length=10)

    class Meta:
        db_table = "lunch_timings"


# class Student(models.Model):


class Student(models.Model):
    rollno = models.CharField(max_length=11)
    kmitrollno = models.CharField(max_length=11)
    name = models.CharField(max_length=100)
    year = models.CharField(max_length=2, default="-1")
    dept = models.CharField(max_length=5)
    section = models.CharField(max_length=5)
    picture = models.CharField(max_length=60, null=True)

    # def json(self):
    #     return

    class Meta:
        db_table = "student"


from ninja import Schema


class ReqPass(Schema):
    roll_no: str
    pass_type: str


class ReqLunchTiming(Schema):
    opening_time: str
    closing_time: str

class ResStudent(Schema):
    rollno : str
    kmitrollno : str
    name : str
    year : str
    dept: str
    section: str
    picture : Union[str , None]




# T = TypeVar('T')
class Result(Schema):
    # content: T | None = None
    success: bool
    msg: str


# initialize students table


def init_students():
    data = []
    with open("./students.json") as file:
        data = list(
            map(
                lambda i: Student(**{
                    "rollno": i["hallticketno"],
                    "name": i["firstname"][:-5],
                    "year":i["currentyear"],
                    "dept": i["dept"],
                    "section": i["section"],
                    "picture": i["picture"],
                }),
                json.loads(file.read()).values(),
            )
        )
    print(())
    Student.objects.bulk_create(
        data
    )
    # Student.objects.bulk_create()
