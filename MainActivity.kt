package com.example.speedometer

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import java.util.Locale

class MainActivity : ComponentActivity() {

    private lateinit var locationManager: LocationManager
    private var speedState = mutableFloatStateOf(0f)

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            startLocationTracking()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        locationManager = getSystemService(Context.LOCATION_SERVICE) as LocationManager

        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    SpeedometerScreen(speedState.floatValue)
                }
            }
        }

        checkPermissionAndStart()
    }

    private fun checkPermissionAndStart() {
        val permissionStatus = ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_FINE_LOCATION
        )

        if (permissionStatus == PackageManager.PERMISSION_GRANTED) {
            startLocationTracking()
        } else {
            permissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
        }
    }

    @SuppressLint("MissingPermission")
    private fun startLocationTracking() {
        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER,
            500L,
            0f,
            object : LocationListener {
                override fun onLocationChanged(location: Location) {
                    if (location.hasSpeed()) {
                        speedState.floatValue = location.speed * 3.6f
                    } else {
                        speedState.floatValue = 0f
                    }
                }
            }
        )
    }
}

@Composable
fun SpeedometerScreen(speed: Float) {
    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier.fillMaxSize()
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = String.format(Locale.US, "%.1f", speed),
                fontSize = 120.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = "км/ч",
                fontSize = 40.sp,
                fontWeight = FontWeight.Medium
            )
        }
    }
}
