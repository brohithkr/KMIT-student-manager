import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart';

import 'secrets.dart';

import './db_handling.dart';
// import 'ffi.dart';

// var hosturl = "http://localhost:3000";

int rollToYear(String rollno) {
  var today = DateTime.now();
  int year = 0;
  year = (today.year - int.parse("20${rollno.substring(0, 2)}"));
  if (today.month > DateTime.september) {
    year += 1;
  }
  return year;
}

dynamic getDecryptedData(String endata) {
  Map res;
  try {
    res = jsonDecode(endata);
    //   if (res.keys.toList() != ["rno", "valid_till"]) {
    //     return null;
  } catch (e) {
    return null;
  }
  return res;
}

Future<bool> isValidPass(rollno) async {
  var passFuture = ValidPass.by(rollno: rollno);
  // var res = await _isValidPass(passFuture);
  var pass = (await passFuture)[0];

  int validTill = (pass['valid_till'] as int);
  var now = DateTime.now();
  if (now.millisecondsSinceEpoch > validTill * 1000) {
    return false;
  }

  int year = rollToYear(pass['rollno'] as String);
  if (pass['pass_type'] == 'alumni' || pass['pass_type'] == 'single_use') {
    print("Is True");
    return true;
  }
  var timing = await getTimings()[year - 1];

  var st_arr = (timing['opening_time'].split(":") as List<String>)
      .map((e) => int.parse(e))
      .toList();
  var en_arr = (timing['closing_time'].split(":") as List<String>)
      .map((e) => int.parse(e))
      .toList();

  int startStamp =
      DateTime(now.year, now.month, now.day, st_arr[0], st_arr[1], 0)
          .millisecondsSinceEpoch;
  int endStamp = DateTime(now.year, now.month, now.day, en_arr[0], en_arr[1], 0)
      .millisecondsSinceEpoch;
  int nowStamp = now.millisecondsSinceEpoch;
  if (!(nowStamp > startStamp && nowStamp < endStamp)) {
    return false;
  }

  return true;
}

// Future<bool> _isValidPass(Future<List<Map<String, Object?>>> passFuture) async {

// }

Future<bool> refresh({bool startup = false}) async {
  if (startup) {
    if (await isDbPresent()) {
      return true;
    }
  }
  try {
    await refreshTimings();
    await ValidPass.loadAll();
    print(await isValidPass("22BD1A0505"));
    return true;
  } catch (e) {
    return false;
  }
}

// Future<bool> refreshStartup() async {
//   if (await isDbPresent()) {
//     return refresh();
//   } else {
//     return
//   }
// }

void main() async {
  String now = (DateTime.now().millisecondsSinceEpoch.toString());
  var res = await http.post(
    Uri.parse("$hostUrl/latecomers"),
    headers: Map<String, String>.from(
      {
        "authorization": "bearer $auth_token",
      },
    ),
    body: jsonEncode(
      [
        {
          "roll_no": "22BD1A0505",
          "date": DateTime.now().millisecondsSinceEpoch.toString(),
        }
      ],
    ),
  );
}
