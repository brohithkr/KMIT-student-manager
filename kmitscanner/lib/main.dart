// ignore_for_file: prefer_const_constructors

import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'color_schemes.g.dart';

import './db_handling.dart' as db;

import './utlis.dart' as utlis;

// class Collection {
//   Future<> is
// }

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  var x = await db.ValidPass.by(rollno: "22BD1A0505");
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
              return Center(
                child: SpinKitCircle(
                  color: Theme.of(context).colorScheme.onBackground,
                  size: 40,
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

  void handleScan(context, toScan) async {
    String scanData = await utlis.scanQR();
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) {
          String initData = scanData;
          return ScanPage(
            toScan: "Scan Latecomers",
            initData: initData,
          );
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
                      handleScan(context, "Scan Passes");
                    },
                  ),
                  MyButton(
                    label: "Scan Latecomers",
                    todo: () {
                      handleScan(context, "Scan Latecomers");
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

class ScanPage extends StatefulWidget {
  const ScanPage({super.key, required this.toScan, required this.initData});
  final String toScan;
  final String initData;

  @override
  State<ScanPage> createState() => _ScanPageState();
}

class _ScanPageState extends State<ScanPage> {
  late String _scanData;

  void handleScan() async {
    String scanData = await utlis.scanQR();
    setState(() {
      _scanData = scanData;
    });
  }

  @override
  void initState() {
    _scanData = widget.initData;
  }

  @override
  Widget build(BuildContext context) {
    if (_scanData == "-1" || _scanData == "--") {
      return Center(
        child: MyButton(
            label: widget.toScan,
            todo: () {
              handleScan();
            }),
      );
    } else {
      // if (widget.toScan == "Scan Passes") {}
      var passFuture = (db.ValidPass.by(rollno: _scanData));
      return FutureBuilder(
          future: passFuture,
          builder: (context, snapshot) {
            var pass = snapshot.data ?? [];
            if (pass.isEmpty) {
              return AffirmBox(isValid: true);
            } else {
              return AffirmBox(isValid: false);
            }
          });
    }
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

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'You have pushed the button this many times:',
            ),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
}
