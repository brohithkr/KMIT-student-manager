from django.db import models


class Latecomers(models.Model):
    roll_no = models.CharField(max_length=11)
    date = models.IntegerField()

    def json(self):
        return {"roll_no": self.roll_no, "date": self.date}

    class Meta:
        db_table = "latecomers"


from ninja import Schema
from typing import List


class Result(Schema):
    success: bool
    msg: str


class ReqLatecomers(Schema):
    roll_no: str
    date: str


class ReqLatecomersList(Schema):
    data: List[ReqLatecomers]
