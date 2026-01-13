[app]
title = Badiboss Eglise
package.name = badiboss_eglise
package.domain = com.badiboss

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
entrypoint = main.py

version = 0.1

requirements = python3==3.11,kivy

orientation = portrait

android.accept_sdk_license = True
android.api = 31
android.minapi = 21

android.sdk_path = /home/useruser/Android
android.ndk_path = /home/useruser/Android/android-ndk-r25c
android.ndk_version = r25c
android.sdkmanager_path = /home/useruser/Android/cmdline-tools/latest/bin/sdkmanager

p4a.branch = master
p4a.extra_args = --storage-dir=/home/useruser/.p4a_storage --color=always

