[app]
title = Simple Solitaire
package.name = simplesolitaire
package.domain = com.timbury
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,md
source.exclude_dirs = .git,.github,.venv,venv,env,tests,dist,build,__pycache__
source.exclude_patterns = .DS_Store,*.pyc,*.pyo,*.spec
version = 0.1.0
requirements = python3,kivy
orientation = landscape
fullscreen = 1

# Optional branding assets (uncomment after adding real files)
# icon.filename = assets/ui/icon.png
# presplash.filename = assets/ui/presplash.png

# Android target configuration
android.api = 34
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

# Build release AAB for Play Store (uncomment when ready)
# android.release_artifact = aab

[buildozer]
log_level = 2
warn_on_root = 1
