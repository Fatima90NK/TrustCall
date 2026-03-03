package com.example.block_spammer_app

import android.content.Intent
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.block_spammer.call_screening"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            if (call.method == "simulateIncomingCall") {
                val number = call.argument<String>("number")
                if (number != null) {
                    CallScreeningService.simulateIncomingCall(this, number)
                    result.success(true)
                } else {
                    result.error("INVALID_ARGUMENT", "Number is required", null)
                }
            } else {
                result.notImplemented()
            }
        }
    }
}
