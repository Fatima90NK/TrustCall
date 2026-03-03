import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:phone_state/phone_state.dart';
import 'call_listener_screen.dart';

void main() {
  runApp(const TrustCallApp());
}

class TrustCallApp extends StatelessWidget {
  const TrustCallApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'TrustCall',
      theme: ThemeData(
        useMaterial3: false,
        fontFamily: 'SF Pro Text',
      ),
      home: const CallListenerScreen(),
    );
  }
}