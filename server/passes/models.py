from django.db import models
from typing import Generic, TypeVar

class IssuedPass(models.Model):
    PASS_TYPES = [
        ("one_time", "one_time"),
        ("daily", "daily"),
        ("alumni", "alumni")
    ]
    roll_no = models.CharField(max_length=11)
    issues_date = models.IntegerField("Unix time stamp of issued date.")
    valid_till = models.IntegerField("Unix time stamp of expiry date.")
    pass_type = models.CharField(choices=PASS_TYPES, max_length=10)

    def json(self):
        return {
            "roll_no": self.roll_no,
            "issue_date": self.issues_date,
            "valid_till": self.valid_till,
            "pass_type": self.pass_type
        }

    class Meta:
        db_table = "issued_pass"

class LunchTiming(models.Model):
    year = models.IntegerField()
    opening_time = models.CharField(max_length=10)
    closing_time = models.CharField(max_length=10)
    
    class Meta:
        db_table = "lunch_timings"

from ninja import Schema


class ReqPass(Schema):
    roll_no: str
    pass_type: str

class ReqLunchTiming(Schema):
    opening_time: str
    closing_time: str

T = TypeVar('T')
class Result(Schema):
    # content: T | None = None
    success: bool
    msg: str
