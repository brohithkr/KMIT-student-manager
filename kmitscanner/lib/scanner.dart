import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:mobile_scanner/mobile_scanner.dart';

class ScanPage extends StatefulWidget {
  const ScanPage({super.key, required this.onScan});

  final Function(String, BuildContext) onScan;

  @override
  State<ScanPage> createState() => ScanPageState();
}

class ScanPageState extends State<ScanPage> {
  late bool toScan;

  void toggleScan() {
    setState(() {
      toScan = !toScan;
    });
  }

  @override
  void initState() {
    super.initState();
    toScan = false;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("scanner"),
      ),
      body: Center(
        child: Stack(
          children: [
            MobileScanner(
              controller: MobileScannerController(
                detectionSpeed: DetectionSpeed.noDuplicates,
              ),
              onDetect: (capture) {
                debugPrint(toScan.toString());
                var barcodes = capture.barcodes;
                debugPrint(barcodes[0].rawValue);
                debugPrint("toScan.toString()");
                if (toScan) {
                  widget.onScan(barcodes[0].rawValue ?? "None", context);
                  toggleScan();
                }
              },
            ),
            RectangleOverlay(toDo: toggleScan),
          ],
        ),
      ),
    );
  }
}

class RectangleOverlay extends StatelessWidget {
  const RectangleOverlay({super.key, required this.toDo});

  final Function toDo;

  @override
  Widget build(BuildContext context) {
    var deviceSize = MediaQuery.of(context).size;
    return Stack(
      alignment: AlignmentDirectional.bottomCenter,
      children: [
        CustomPaint(
          size: deviceSize,
          painter: OverlayPainter(
            holeSize: Size(
              deviceSize.width * 6 / 8,
              deviceSize.width * 6 / 8,
              // deviceSize.height * 2.5 / 8,
            ),
          ),
        ),
        IconButton(
          onPressed: () {
            HapticFeedback.vibrate();
            toDo();
          },
          icon: Icon(
            Icons.camera,
            color: Colors.white,
            size: deviceSize.width / 6,
          ),
        ),
      ],
    );
  }
}

class OverlayPainter extends CustomPainter {

  Size holeSize;
  OverlayPainter({required this.holeSize});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = Color.fromARGB(121, 0, 0, 0);

    canvas.drawPath(
      Path.combine(
        PathOperation.difference,
        Path()..addRect(Rect.fromLTWH(0, 0, size.width, size.height)),
        Path()
          ..addRRect(RRect.fromRectAndRadius(
            Rect.fromLTWH(
              size.width / 8,
              size.height / 8,
              holeSize.width,
              holeSize.height,
            ),
            Radius.circular(10),
          )),
      ),
      paint,
    );
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) {
    return false;
  }
}