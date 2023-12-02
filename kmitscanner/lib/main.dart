// ignore_for_file: prefer_const_constructors

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'color_schemes.g.dart';
import 'package:path_provider/path_provider.dart';

import './db_handling.dart' as db;
import './scanner.dart';

import './utlis.dart' as utlis;

// class Collection {
//   Future<> is
// }

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  if (Platform.isAndroid) {
    final dir = await getApplicationDocumentsDirectory();
    final path = dir.parent.path;
    final file =
        File('$path/databases/com.google.android.datatransport.events');
    await file.writeAsString('Fake');
  }
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    String title = "Kmit Scanner";
    Future<bool> loaded = utlis.refresh();

    return MaterialApp(
      title: title,
      theme: ThemeData(
        colorScheme: lightColorScheme,
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: darkColorScheme,
        useMaterial3: true,
      ),
      home: FutureBuilder<bool>(
          initialData: null,
          future: loaded,
          builder: (context, snapshot) {
            if (snapshot.data == null) {
              return Scaffold(
                body: Center(
                  child: SpinKitCircle(
                    color: Theme.of(context).colorScheme.onBackground,
                    size: 40,
                  ),
                ),
              );
            }
            return HomePage(title: title);
          }),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key, required this.title});
  final String title;

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  // late String _scanData;

  void handleScan(
      context, title, Future<bool> Function(String) affirmFun) async {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) {
          return ScanPage(
              title: title,
              onScan: (scanRes, context) {
                var deviceSize = MediaQuery.of(context).size;
                showDialog(
                  context: context,
                  builder: (context) {
                    var affirm = affirmFun(scanRes);
                    return FutureBuilder(
                        future: affirm,
                        builder: (context, snap) {
                          return AffirmBox(isValid: snap.data ?? false);
                        });
                  },
                );
              });
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: Icon(Icons.arrow_back),
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          children: [
            Flexible(flex: 2, fit: FlexFit.tight, child: SizedBox()),
            Flexible(
              flex: 2,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  MyButton(
                    label: "Scan Passes",
                    todo: () {
                      handleScan(context, "Scan Passes", utlis.isValidPass);
                    },
                  ),
                  MyButton(
                    label: "Scan Latecomers",
                    todo: () {
                      handleScan(context, "Scan Latecomers", utlis.isValidPass);
                    },
                  )
                ],
              ),
            ),
            Flexible(flex: 4, fit: FlexFit.tight, child: SizedBox()),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          await utlis.refresh();
        },
        child: Icon(Icons.refresh),
        // shape: ,
      ),
    );
  }
}


class AffirmBox extends StatelessWidget {
  const AffirmBox({super.key, required this.isValid});
  final bool isValid;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        AffirmIcon(isValid: isValid),
      ],
    );
  }
}

class AffirmIcon extends StatelessWidget {
  const AffirmIcon({required this.isValid, super.key});
  final bool isValid;

  final Color green = const Color.fromARGB(255, 7, 141, 63);
  final Color red = const Color.fromARGB(255, 186, 49, 49);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsetsDirectional.symmetric(vertical: 25),
      decoration: BoxDecoration(
        color: ((isValid) ? green : red),
        shape: BoxShape.circle,
      ),
      child: Icon(
        (isValid) ? Icons.done_rounded : Icons.close_rounded,
        color: Colors.white,
        size: 80,
      ),
    );
  }
}

class MyButton extends StatelessWidget {
  const MyButton({super.key, required this.label, required this.todo});
  final String label;
  final void Function() todo;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(15),
      child: ElevatedButton(
        onPressed: todo,
        child: Padding(
          padding: const EdgeInsets.all(5),
          child: Text(
            label,
            style: TextStyle(
              fontSize: 25,
              // fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }
}