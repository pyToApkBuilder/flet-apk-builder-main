[app]
title = stockvision
package.name = stockVision
package.domain = org.aritra
source.include_exts = py,png,jpg,jpeg,kv,txt
version = 1.0
requirements = python3, kivy==2.3.1, yfinance, pandas, numpy, requests,pillow, certifi
orientation = portrait
osx.kivy_version = 2.3.1

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.arch = arm64-v8a, armeabi-v7a
android.permissions = INTERNET

source.include_patterns = assets/*
android.enable_androidx = True
android.gradle_dependencies = com.google.android.material:material:1.1.0

[buildozer]
log_level = 2
warn_on_root = 1
