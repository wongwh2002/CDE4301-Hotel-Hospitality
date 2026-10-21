package com.example.rokid_app

import android.app.Application
import androidx.camera.camera2.Camera2Config
import androidx.camera.core.CameraXConfig

class RokidApplication : Application(), CameraXConfig.Provider {
    override fun getCameraXConfig(): CameraXConfig = Camera2Config.defaultConfig()
}
