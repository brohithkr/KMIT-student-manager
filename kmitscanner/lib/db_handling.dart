import 'dart:async';

import 'dart:convert';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

import 'package:http/http.dart' as http;
import 'secrets.dart';

void createTables(Database db) {
  // db.execute('CREATE TABLE latecomers (rollno varchar(11), date integer)');
  db.execute('''CREATE TABLE valid_pass (
    rollno varchar(11),
    issue_date BIGINT,
    valid_till BIGINT
  )''');
  db.execute('''CREATE TABLE Lunch_Timings (
        year varchar(2) UNIQUE,
        opening_time varchar(7),
        closing_time varchar(7)
    );''');
  db.execute(
      "INSERT INTO Lunch_Timings (year,opening_time,closing_time) VALUES ('1', '12:15', '13:00')");
  db.execute(
      "INSERT INTO Lunch_Timings (year,opening_time,closing_time) VALUES ('2', '12:15', '13:00')");
  db.execute(
      "INSERT INTO Lunch_Timings (year,opening_time,closing_time) VALUES ('3', '12:15', '13:00')");
}

Future<Database> openDB() async {
  // await databaseFactory
  //     .deleteDatabase(join(await getDatabasesPath(), 'data.db'));
  final database = openDatabase(
    join(await getDatabasesPath(), 'data.db'),
    onCreate: (db, version) {
      createTables(db);
    },
    version: 1,
  );
  return database;
}

class ValidPass {
  String rollno;
  BigInt issue_date;
  BigInt valid_till;
  ValidPass(this.rollno, this.issue_date, this.valid_till);

  static const tablename = "valid_pass";

  Map<String, dynamic> toMap() {
    return {
      "rollno": rollno,
      "issue_date": issue_date,
      "valid_till": valid_till,
    };
  }

  Future<List<Map<String, Object?>>> by({required String rollno}) async {
    final db = await openDB();
    var res = await db.query(tablename,
        columns: null, where: "rollno = ?", whereArgs: [rollno]);
    return res;
  }

  Future<bool> insertToDB() async {
    try {
      var db = await openDB();
      await db.insert(tablename, toMap());
      // var res = await db.query("Lunch_Timings");
      // print(res);
      return true;
    } catch (e) {
      return false;
    }
  }

  static Future<bool> loadAll() async {
    try {
      var db = await openDB();
      var res = await http.get(Uri.parse("$hostUrl/get_valid_passes"));
      db.insert(tablename, jsonDecode(res.body));
      return true;
    } catch (e) {
      return false;
    }
  }
}

dynamic getTimings() async {
  final db = await openDB();
  var res = await db.query("Lunch_Timings");
  return res;
}

void refreshTimings() async {
  var res = await http.get(Uri.parse('$hostUrl/get_timings'));
  var timings = jsonDecode(res.body);
  var db = await openDB();
  for (var i in timings) {
    db.update("Lunch_Timings", i, where: 'year = ?', whereArgs: [i['year']]);
  }
}
