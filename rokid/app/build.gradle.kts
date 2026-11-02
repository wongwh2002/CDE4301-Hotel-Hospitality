plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.example.rokid_app"
    compileSdk = 37

    defaultConfig {
        applicationId = "com.example.rokid_app"
        minSdk = 29
        targetSdk = 37
        versionCode = 3
        versionName = "3.0-faces"
        val serverUrl = providers.gradleProperty("faceServerUrl").orElse(providers.gradleProperty("objectServerUrl")).orElse("http://127.0.0.1:8000").get()
        buildConfigField("String", "FACE_SERVER_URL", "\"" + serverUrl.replace("\\", "\\\\").replace("\"", "\\\"") + "\"")
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildFeatures { buildConfig = true }
    buildTypes {
        release {
            optimization {
                enable = true
                packageScope = setOf("androidx.**", "kotlin.**", "kotlinx.**")
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    implementation(libs.mlkit.face.detection)
    implementation(libs.androidx.appcompat)
    implementation(libs.androidx.core.ktx)
    implementation(libs.material)
    implementation(libs.androidx.camera.core)
    implementation(libs.androidx.camera.camera2)
    implementation(libs.androidx.camera.lifecycle)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.junit)
}
