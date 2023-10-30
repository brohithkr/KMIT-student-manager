from django.db import models


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

    class Meta:
        db_table = "Issued_Pass"


from ninja import Schema

class ReqPass(Schema):
    roll_no: str
    pass_type: str
