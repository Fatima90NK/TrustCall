import 'dart:async';
import 'package:flutter/material.dart';
import 'package:phone_state/phone_state.dart';

class TrustCallScreen extends StatefulWidget {
  final String callerNumber;
  final Map<String, dynamic>? trustData;

  const TrustCallScreen({
    super.key,
    required this.callerNumber,
    required this.trustData,
  });

  @override
  State<TrustCallScreen> createState() => _TrustCallScreenState();
}

class _TrustCallScreenState extends State<TrustCallScreen> {
  StreamSubscription? _subscription;

  // ── Parse from real API response ──────────────────────────────────────────
  bool get isLoading => widget.trustData == null;

  // "CAUTION", "SAFE", "DANGER" etc
  String get badge =>
      (widget.trustData?['badge'] ?? '...').toString().toUpperCase();

  // 0 - 100
  int get compositeScore =>
      (widget.trustData?['composite_score'] ?? 0) as int;

  // Badge → color
  Color get badgeColor {
    switch (badge) {
      case 'SAFE':
        return const Color(0xFF28C262);
      case 'CAUTION':
        return const Color(0xFFE5943E);
      case 'DANGER':
        return const Color(0xFFB43133);
      default:
        return Colors.grey;
    }
  }

  // Badge → icon
  IconData get badgeIcon {
    switch (badge) {
      case 'SAFE':
        return Icons.check_circle_rounded;
      case 'CAUTION':
        return Icons.warning_amber_rounded;
      case 'DANGER':
        return Icons.dangerous_rounded;
      default:
        return Icons.help_outline_rounded;
    }
  }

  // Badge → message
  String get badgeMessage {
    switch (badge) {
      case 'SAFE':
        return 'This number appears to be trustworthy.';
      case 'CAUTION':
        return 'This call is flagged and is likely to be fraudulent.';
      case 'DANGER':
        return 'This number is highly dangerous. Do not answer.';
      default:
        return 'Unable to verify this number.';
    }
  }

  // Score label
  String get scoreLabel {
    if (compositeScore >= 70) return 'TRUSTED';
    if (compositeScore >= 40) return 'CAUTION';
    return 'FLAGGED';
  }

  Color get scoreColor {
    if (compositeScore >= 70) return const Color(0xFF28C262);
    if (compositeScore >= 40) return const Color(0xFFE5943E);
    return const Color(0xFFE54C4C);
  }

  @override
  void initState() {
    super.initState();
    _subscription = PhoneState.stream.listen((event) {
      if (event.status == PhoneStateStatus.CALL_ENDED ||
          event.status == PhoneStateStatus.NOTHING) {
        if (mounted) Navigator.of(context).pop();
      }
    });
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: Colors.black,
      body: Container(
        width: size.width,
        height: size.height,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF171822), Color(0xFF050507)],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding:
                const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const SizedBox(height: 8),
                const Text(
                  'AI Result Analysis',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    letterSpacing: 0.5,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Verification Analysis for Caller Number:',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.65),
                    fontSize: 14,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 4),
                Text(
                  widget.callerNumber,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    letterSpacing: 1.0,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 32),

                // ── Main Card ──────────────────────────────────────────────
                Container(
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: const Color(0xFF181922).withOpacity(0.95),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: const [
                      BoxShadow(
                        color: Colors.black54,
                        blurRadius: 24,
                        offset: Offset(0, 16),
                      ),
                    ],
                  ),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 18.0, vertical: 16.0),
                  child: isLoading
                      ? _buildLoadingState()
                      : _buildResultState(),
                ),

                const Spacer(),

                // ── Bottom Call Controls ───────────────────────────────────
                Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 18, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF14151C).withOpacity(0.9),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Row(
                    children: [
                      // Decline
                      Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          GestureDetector(
                            onTap: () => Navigator.of(context).pop(),
                            child: Container(
                              width: 60,
                              height: 60,
                              decoration: const BoxDecoration(
                                shape: BoxShape.circle,
                                color: Color(0xFFE5453E),
                              ),
                              child: const Icon(Icons.call_end,
                                  size: 28, color: Colors.white),
                            ),
                          ),
                          const SizedBox(height: 4),
                          const Text('Decline',
                              style: TextStyle(
                                  color: Colors.white70, fontSize: 13)),
                        ],
                      ),

                      const Expanded(
                        child: Center(
                          child: Text(
                            'slide to answer',
                            style: TextStyle(
                                color: Colors.white70, fontSize: 16),
                          ),
                        ),
                      ),

                      // Accept
                      Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          GestureDetector(
                            onTap: () => Navigator.of(context).pop(),
                            child: Container(
                              width: 60,
                              height: 60,
                              decoration: const BoxDecoration(
                                shape: BoxShape.circle,
                                color: Color(0xFF28C262),
                              ),
                              child: const Icon(Icons.call,
                                  size: 28, color: Colors.white),
                            ),
                          ),
                          const SizedBox(height: 4),
                          const Text('Accept',
                              style: TextStyle(
                                  color: Colors.white70, fontSize: 13)),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ── Loading state ──────────────────────────────────────────────────────────
  Widget _buildLoadingState() {
    return Column(
      children: [
        _buildHeader(),
        const SizedBox(height: 24),
        const CircularProgressIndicator(color: Color(0xFFFF7A4C)),
        const SizedBox(height: 16),
        Text(
          'Analyzing caller...',
          style: TextStyle(
              color: Colors.white.withOpacity(0.6), fontSize: 14),
        ),
        const SizedBox(height: 24),
      ],
    );
  }

  // ── Result state ───────────────────────────────────────────────────────────
  Widget _buildResultState() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildHeader(),
        const SizedBox(height: 18),

        // Badge warning box
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: const Color(0xFF20212B),
            borderRadius: BorderRadius.circular(16),
          ),
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: badgeColor.withOpacity(0.2),
                      border: Border.all(color: badgeColor, width: 1.5),
                    ),
                    child: Icon(badgeIcon, size: 18, color: badgeColor),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      badgeMessage,
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.88),
                        fontSize: 14,
                        height: 1.3,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Badge pill
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 14, vertical: 4),
                decoration: BoxDecoration(
                  color: badgeColor,
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  badge,                          // ✅ "CAUTION" / "SAFE" / "DANGER"
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.2,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),

        // Composite score row
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(7),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: scoreColor.withOpacity(0.15),
                border: Border.all(color: scoreColor, width: 1.5),
              ),
              child:
                  Icon(Icons.shield_rounded, size: 18, color: scoreColor),
            ),
            const SizedBox(width: 12),
            const Text(
              'Trust Score:',
              style: TextStyle(
                  color: Colors.white70,
                  fontSize: 14,
                  fontWeight: FontWeight.w500),
            ),
            const SizedBox(width: 4),
            Text(
              '$compositeScore',              // ✅ real composite score
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.w600),
            ),
            const SizedBox(width: 4),
            Text(
              scoreLabel,                     // ✅ TRUSTED / CAUTION / FLAGGED
              style: TextStyle(
                  color: scoreColor,
                  fontSize: 14,
                  fontWeight: FontWeight.w600),
            ),
            const Spacer(),
            Icon(Icons.chevron_right_rounded,
                color: Colors.white.withOpacity(0.7)),
          ],
        ),
        const SizedBox(height: 18),
        Text(
          'Detailed Analysis',
          style:
              TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 14),
        ),
      ],
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(10),
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFFFF7A4C), Color(0xFFD63A2C)],
            ),
          ),
          child: const Icon(Icons.phone, size: 18, color: Colors.white),
        ),
        const SizedBox(width: 10),
        const Text(
          'TrustCall',
          style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.w600),
        ),
      ],
    );
  }
}