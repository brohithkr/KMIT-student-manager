// ignore_for_file: prefer_const_constructors, prefer_const_literals_to_create_immutables

import 'package:flutter/material.dart';
import './db_handling.dart';

import './utlis.dart' as utlis;

void main() async {
  // await ValidPass.loadAll();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    String title = "Kmit Scanner";

    return MaterialApp(
      title: title,
      theme: ThemeData(
        colorScheme:
            ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 58, 106, 183)),
        useMaterial3: true,
      ),
      home: HomePage(title: title),
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
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: Icon(Icons.arrow_back),
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            MyButton(
              label: "Scan Passes",
              todo: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) {
                      String initData = utlis.scanQR();
                      return ScanPage(
                          toScan: "Scan Passes", initData: initData);
                    },
                  ),
                );
              },
            ),
            MyButton(
              label: "Scan Latecomers",
              todo: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) {
                      String initData = utlis.scanQR();
                      return ScanPage(
                          toScan: "Scan Latecomers", initData: initData);
                    },
                  ),
                );
              },
            )
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
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
      return Placeholder();
    }
  }
}

class MyButton extends StatelessWidget {
  const MyButton({super.key, required this.label, required this.todo});
  final String label;
  final void Function() todo;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: ElevatedButton(
        onPressed: todo,
        child: Padding(
          padding: const EdgeInsets.all(5),
          child: Text(
            label,
            style: TextStyle(
              fontSize: 18,
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
