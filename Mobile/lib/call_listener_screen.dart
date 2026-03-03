import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:permission_handler/permission_handler.dart';
import 'package:phone_state/phone_state.dart';
import 'trust_call_screen.dart';

// ── Config ─────────────────────────────────────────────────────────────────
const String kBackendBaseUrl = "http://34.175.180.5:8000";

class CallListenerScreen extends StatefulWidget {
  const CallListenerScreen({super.key});

  @override
  State<CallListenerScreen> createState() => _CallListenerScreenState();
}

class _CallListenerScreenState extends State<CallListenerScreen> {
  StreamSubscription? _phoneSubscription;
  bool _hasPermission = false;
  bool _isListening = false;
  bool _isAnalyzing = false;
  String? _lastCallerNumber;

  @override
  void initState() {
    super.initState();
    _requestAndListen();
  }

  @override
  void dispose() {
    _phoneSubscription?.cancel();
    super.dispose();
  }

  // ── 1. Request permission + start listening ─────────────────────────────
  Future<void> _requestAndListen() async {
    final status = await Permission.phone.request();

    if (!status.isGranted) {
      setState(() => _hasPermission = false);
      return;
    }

    setState(() {
      _hasPermission = true;
      _isListening = true;
    });

    _startPhoneListener();
  }

  // ── 2. Listen to phone state changes ───────────────────────────────────
  void _startPhoneListener() {
    _phoneSubscription = PhoneState.stream.listen((PhoneState event) async {
      switch (event.status) {

        case PhoneStateStatus.CALL_INCOMING:
          final number = (event.number != null && event.number!.isNotEmpty)
              ? event.number!
              : 'Unknown Number';

          // Avoid duplicate triggers for same call
          if (_lastCallerNumber == number && _isAnalyzing) return;
          _lastCallerNumber = number;

          await _analyzeAndShow(number);
          break;

        case PhoneStateStatus.CALL_ENDED:
        case PhoneStateStatus.NOTHING:
          _lastCallerNumber = null;
          setState(() => _isAnalyzing = false);
          break;

        case PhoneStateStatus.CALL_STARTED:
          // Call was answered — nothing to do
          break;
      }
    });
  }

  // ── 3. Show TrustCall screen + run API in background ───────────────────
  Future<void> _analyzeAndShow(String number) async {
    if (!mounted) return;
    setState(() => _isAnalyzing = true);

    // Show screen immediately with loading spinner
    Navigator.of(context).push(
      PageRouteBuilder(
        pageBuilder: (_, __, ___) => TrustCallScreen(
          callerNumber: number,
          trustData: null,        // null = show loading spinner
        ),
        transitionsBuilder: (_, animation, __, child) => SlideTransition(
          position: Tween<Offset>(
            begin: const Offset(0, 1),
            end: Offset.zero,
          ).animate(CurvedAnimation(
            parent: animation,
            curve: Curves.easeOut,
          )),
          child: child,
        ),
      ),
    );

    // Call API in background while spinner shows
    final result = await _callTrustHandshake(number);

    if (!mounted) return;
    setState(() => _isAnalyzing = false);

    // Replace loading screen with real data screen
    Navigator.of(context).pushReplacement(
      PageRouteBuilder(
        pageBuilder: (_, __, ___) => TrustCallScreen(
          callerNumber: number,
          trustData: result,      // real API response
        ),
        transitionsBuilder: (_, animation, __, child) => FadeTransition(
          opacity: animation,
          child: child,
        ),
      ),
    );
  }

  // ── 4. POST to backend (which calls TrustCall API) ────────────────
  Future<Map<String, dynamic>?> _callTrustHandshake(String number) async {
    try {
      final response = await http.post(
        Uri.parse('$kBackendBaseUrl/v1/trust-handshake'),   // ← your backend middleman
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': 'local-dev-trustcall-key'
        },
        body: jsonEncode({
          'phone_number': number,
        }),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        debugPrint('✅ TrustCall response: $data');
        return data;
      } else {
        debugPrint('❌ TrustCall error ${response.statusCode}: ${response.body}');
        return null;
      }

    } on TimeoutException {
      debugPrint('❌ TrustCall timeout');
      return null;
    } catch (e) {
      debugPrint('❌ TrustCall exception: $e');
      return null;
    }
  }

  // ── UI ──────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF050507),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [

            // Logo
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0xFFFF7A4C), Color(0xFFD63A2C)],
                ),
              ),
              child: const Icon(Icons.phone, size: 36, color: Colors.white),
            ),
            const SizedBox(height: 20),

            const Text(
              'TrustCall',
              style: TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),

            // Status indicator
            _buildStatusIndicator(),
            const SizedBox(height: 32),

            // Permission button (only shown if not granted)
            if (!_hasPermission)
              ElevatedButton.icon(
                onPressed: _requestAndListen,
                icon: const Icon(Icons.security),
                label: const Text('Grant Phone Permission'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFD63A2C),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                      horizontal: 32, vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusIndicator() {
    String label;
    Color color;
    Widget? leading;

    if (!_hasPermission) {
      label = 'Permission required';
      color = Colors.red;
      leading = const Icon(Icons.cancel, size: 12, color: Colors.red);
    } else if (_isAnalyzing) {
      label = 'Analyzing incoming call...';
      color = const Color(0xFFFF7A4C);
      leading = const SizedBox(
        width: 12,
        height: 12,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          color: Color(0xFFFF7A4C),
        ),
      );
    } else if (_isListening) {
      label = 'Listening for incoming calls...';
      color = const Color(0xFF28C262);
      leading = Container(
        width: 8,
        height: 8,
        decoration: const BoxDecoration(
          shape: BoxShape.circle,
          color: Color(0xFF28C262),
        ),
      );
    } else {
      label = 'Not listening';
      color = Colors.grey;
      leading = Container(
        width: 8,
        height: 8,
        decoration: const BoxDecoration(
          shape: BoxShape.circle,
          color: Colors.grey,
        ),
      );
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        ...[
        leading,
        const SizedBox(width: 6),
      ],
        Text(
          label,
          style: TextStyle(
            color: color.withOpacity(0.8),
            fontSize: 14,
          ),
        ),
      ],
    );
  }
}