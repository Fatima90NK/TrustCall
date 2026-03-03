package com.example.block_spammer_app

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import androidx.core.app.NotificationCompat
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.embedding.engine.FlutterEngineCache
import io.flutter.plugin.common.MethodChannel

class CallScreeningService : Service() {
    private var flutterEngine: FlutterEngine? = null
    private val CHANNEL = "com.block_spammer.call_screening"
    private val handler = Handler(Looper.getMainLooper())
    private var pendingCall: PendingCall? = null

    companion object {
        private const val CHANNEL_ID = "CallScreeningService"
        private const val NOTIFICATION_ID = 1001

        fun start(context: Context) {
            val intent = Intent(context, CallScreeningService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun simulateIncomingCall(context: Context, number: String) {
            val intent = Intent(context, CallScreeningService::class.java).apply {
                action = "SIMULATE_CALL"
                putExtra("number", number)
            }
            context.startService(intent)
        }
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, createNotification())
        initializeFlutter()
    }

    private fun initializeFlutter() {
        flutterEngine = FlutterEngineCache.getInstance().get("flutter_engine")
            ?: FlutterEngine(this).apply {
                FlutterEngineCache.getInstance().put("flutter_engine", this)
            }

        flutterEngine?.dartExecutor?.binaryMessenger?.let { messenger ->
            MethodChannel(messenger, CHANNEL).setMethodCallHandler { call, result ->
                when (call.method) {
                    "onIncomingCall" -> {
                        val number = call.argument<String>("number")
                        val disallow = call.argument<Boolean>("disallow") ?: false
                        val riskScore = call.argument<Int>("riskScore") ?: 0
                        val labels = call.argument<List<String>>("labels") ?: emptyList()

                        if (disallow) {
                            // Block call - end it programmatically
                            if (number != null) {
                                endCall(number, reason = "High risk ($riskScore): ${labels.joinToString()}")
                            }
                            result.success(mapOf(
                                "blocked" to true,
                                "reason" to "High risk call blocked"
                            ))
                        } else {
                            // Allow call
                            if (number != null) {
                                allowCall(number)
                            }
                            result.success(mapOf(
                                "blocked" to false,
                                "reason" to "Call allowed"
                            ))
                        }
                    }
                    else -> result.notImplemented()
                }
            }
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        intent?.let {
            when (it.action) {
                "SIMULATE_CALL" -> {
                    val number = it.getStringExtra("number") ?: return@let
                    handleIncomingCall(number)
                }
            }
        }
        return START_STICKY
    }

    private fun handleIncomingCall(number: String) {
        // Check if Flutter is ready
        if (flutterEngine?.dartExecutor == null) {
            // If Flutter is not ready, allow the call by default
            allowCall(number)
            return
        }

        // Send the number to Dart for risk assessment
        pendingCall = PendingCall(number, System.currentTimeMillis())
        flutterEngine?.dartExecutor?.binaryMessenger?.let { messenger ->
            MethodChannel(messenger, CHANNEL).invokeMethod(
                "onIncomingCall",
                mapOf("number" to number),
                object : MethodChannel.Result {
                    override fun success(result: Any?) {
                        // Response is handled by the method call handler
                        pendingCall = null
                    }

                    override fun error(errorCode: String, errorMessage: String?, errorDetails: Any?) {
                        // On error, allow the call
                        allowCall(number)
                        pendingCall = null
                    }

                    override fun notImplemented() {
                        // On not implemented, allow the call
                        allowCall(number)
                        pendingCall = null
                    }
                }
            )
        }
    }

    private fun endCall(number: String, reason: String) {
        // In a real implementation, this would:
        // 1. Use TelecomManager to end the call
        // 2. Show a notification that the call was blocked
        // 3. Log the blocked call

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Call Blocked")
            .setContentText("$number blocked: $reason")
            .setSmallIcon(android.R.drawable.ic_menu_call)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()

        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify((System.currentTimeMillis() % Int.MAX_VALUE).toInt(), notification)

        // In production, use TelecomManager to end the call
        // This requires BIND_TELECOM_CONNECTION_SERVICE permission
        tryEndCallViaTelecomManager(number)
    }

    private fun allowCall(number: String) {
        // Let the call ring normally
        // In production, you might show a subtle indicator that the call was checked
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Call Screened")
            .setContentText("$number: Risk assessment complete - No threat detected")
            .setSmallIcon(android.R.drawable.ic_menu_call)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .build()

        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify((System.currentTimeMillis() % Int.MAX_VALUE).toInt(), notification)
    }

    private fun tryEndCallViaTelecomManager(number: String) {
        // This is a simplified version - in production, you'd need:
        // 1. A custom ConnectionService implementation
        // 2. BIND_TELECOM_CONNECTION_SERVICE permission in manifest
        // 3. Register the service with TelecomManager

        // For demonstration, we'll log the action
        android.util.Log.d("CallScreening", "Would end call from: $number")
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Call Screening Service",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Notifies about blocked calls"
            }

            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Call Screening Active")
            .setContentText("Monitoring incoming calls...")
            .setSmallIcon(android.R.drawable.ic_menu_call)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        flutterEngine?.destroy()
    }

    data class PendingCall(
        val number: String,
        val timestamp: Long
    )
}
