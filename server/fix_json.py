import json

data = {}

def fix_3rd_yr_rno(key):
    rno = (key["picture"]).split("/")[-1].split(".")[0]
    # print(f'{rno} is being changed')
    key["hallticketno"] = rno
    return key

def fix_1st_yr_photo_url(key):
    rno = key["hallticketno"]
    key["picture"] += f"{rno}.jpg"
    return key

def fix_issues(data: dict):
    for i in range(len(data)):
        if (data[i]["picture"]).split("/")[-1] == '' :
            # print(data[i]["hallticketno"][0:2] == "23")
            # print(data[i]["hallticketno"], data[i]["hallticketno"][0:2])
            if data[i]["hallticketno"][0:2] == "23":
                data[i] = fix_1st_yr_photo_url(data[i])
        if (data[i]["picture"]).split("/")[-1].split(".")[0][0:2] == "21":
            data[i] = fix_3rd_yr_rno(data[i])
    return data

with open("./students.json") as dataf:
    data = json.load(dataf)

data = fix_issues(data)
with open("./students.json", "w") as f:
    json.dump(data,f, indent=3)



        
