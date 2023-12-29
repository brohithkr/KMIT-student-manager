// ignore_for_file: prefer_const_constructors

import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

import 'package:qr_mobile_vision/qr_camera.dart';

class ScanPage extends StatefulWidget {
  const ScanPage({super.key, required this.title, required this.onScan});

  final Function(String, BuildContext) onScan;
  final String title;

  @override
  State<ScanPage> createState() => ScanPageState();
}

class ScanState {
  var toScan = ValueNotifier(false);
  void toggleScan() {
    toScan.value = !toScan.value;
  }
}

class ScanPageState extends State<ScanPage> {
  late ValueNotifier<bool> toScan;

  void toggleScan() {
    toScan.value = !toScan.value;
  }

  @override
  void initState() {
    super.initState();
    toScan = ValueNotifier(false);
  }

  @override
  void dispose() {
    toScan.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    var deviceSize = MediaQuery.of(context).size;
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Stack(
          children: [
            QrCamera(
              qrCodeCallback: (code) {
                // var barcodes = code;
                // debugPrint(barcodes);
                if (toScan.value) {
                  widget.onScan(code ?? "None", context);
                  toggleScan();
                }
              },
              notStartedBuilder: (context) {
                return Container(color: Color(0x00000000), height: deviceSize.height, width: deviceSize.width);
              },
            ),
            const RectangleOverlay(),
            Column(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Stack(
                  children: [
                    Align(
                      alignment: Alignment.bottomLeft,
                      child: FlashButton(
                        deviceSize: deviceSize,
                        toDo: () {
                          QrCamera.toggleFlash();
                        },
                      ),
                    ),
                    Align(
                      alignment: Alignment.bottomCenter,
                      child: ValueListenableBuilder(
                          valueListenable: toScan,
                          builder: (context, toScan, widget) {
                            return ThemedButton(
                              toDo: () {
                                if (!toScan) {
                                  toggleScan();
                                }
                              },
                              deviceSize: deviceSize,
                              icon: (toScan)
                                  ? SpinKitFadingCircle(
                                      color: Colors.white,
                                      size: ((deviceSize.width / 8) < 90)
                                          ? deviceSize.width / 8
                                          : 90,
                                    )
                                  : Icon(
                                      Icons.camera_alt_rounded,
                                      color: Colors.white,
                                      size: ((deviceSize.width / 8) < 90)
                                          ? deviceSize.width / 8
                                          : 90,
                                    ),
                            );
                          }),
                    ),
                  ],
                ),
                SizedBox(height: deviceSize.height / 8),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class RectangleOverlay extends StatelessWidget {
  const RectangleOverlay({super.key});

  @override
  Widget build(BuildContext context) {
    var deviceSize = MediaQuery.of(context).size;
    var holeSize = Size(
      deviceSize.width * 6 / 8,
      deviceSize.width * 6 / 8,
    );
    return ClipPath(
      clipper: OverlayClipper(holeSize: holeSize),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 6, sigmaY: 6),
        child: Stack(
          alignment: AlignmentDirectional.bottomCenter,
          children: [
            CustomPaint(
              size: deviceSize,
              painter: OverlayPainter(
                holeSize: holeSize,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class FlashButton extends StatelessWidget {
  const FlashButton({
    super.key,
    required this.toDo,
    required this.deviceSize,
  });

  final Function toDo;
  final Size deviceSize;

  @override
  Widget build(BuildContext context) {
    return ThemedButton(
      icon: Icon(
        Icons.flash_on,
        color: Colors.white,
        size: ((deviceSize.width / 8) < 90) ? deviceSize.width / 8 : 90,
      ),
      toDo: toDo,
      deviceSize: deviceSize,
    );
  }
}

class ThemedButton extends StatelessWidget {
  const ThemedButton({
    super.key,
    required this.icon,
    required this.toDo,
    required this.deviceSize,
  });
  final Widget icon;
  final Function toDo;
  final Size deviceSize;

  @override
  Widget build(BuildContext context) {
    return RawMaterialButton(
      onPressed: () {
        HapticFeedback.vibrate();
        toDo();
      },
      shape: const CircleBorder(),
      fillColor: const Color.fromARGB(100, 0, 0, 0),
      splashColor: const Color.fromARGB(255, 0, 0, 0),
      focusColor: const Color.fromARGB(255, 0, 0, 0),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: icon,
      ),
    );
  }
}

class OverlayPainter extends CustomPainter {
  Size holeSize;
  OverlayPainter({required this.holeSize});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = const Color.fromARGB(121, 0, 0, 0);

    canvas.drawPath(
      Path.combine(
        PathOperation.difference,
        Path()..addRect(Rect.fromLTWH(0, 0, size.width, size.height)),
        Path()
          ..addRRect(
            RRect.fromRectAndRadius(
              Rect.fromLTWH(
                size.width / 8,
                size.height / 8,
                holeSize.width,
                holeSize.height,
              ),
              const Radius.circular(10),
            ),
          ),
      ),
      paint,
    );
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) {
    return false;
  }
}

class OverlayClipper extends CustomClipper<Path> {
  OverlayClipper({required this.holeSize});

  Size holeSize;

  @override
  Path getClip(Size size) {
    return Path.combine(
      PathOperation.difference,
      Path()..addRect(Rect.fromLTWH(0, 0, size.width, size.height)),
      Path()
        ..addRRect(
          RRect.fromRectAndRadius(
            Rect.fromLTWH(
              size.width / 8,
              size.height / 8,
              holeSize.width,
              holeSize.height,
            ),
            const Radius.circular(10),
          ),
        ),
    );
  }

  @override
  bool shouldReclip(covariant CustomClipper oldClipper) => false;
}
