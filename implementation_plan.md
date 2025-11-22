# Implementation Plan - Android Conversion

The goal is to package the existing Flask web application (`agri_dash.py`) as an Android APK. We will use **Kivy** and **Buildozer** to create a wrapper that runs the Flask server locally on the device and displays it in a WebView (or system browser).

## User Review Required
> [!WARNING]
> **TensorFlow Compatibility**: Running full TensorFlow on Android via Buildozer is complex and may result in a very large APK or build failures. We will attempt to include it, but if it fails, we may need to switch to `tflite-runtime` or disable ML features on mobile.

> [!IMPORTANT]
> **Build Environment**: You (the user) will need a Linux environment (or WSL on Windows) to run `buildozer android debug`. Buildozer does not run natively on Windows PowerShell.

## Proposed Changes

### Core Application
#### [MODIFY] [agri_dash.py](file:///d:/final%20project/agri_dash.py)
- Update file paths (models, database) to use `os.path.dirname(os.path.abspath(__file__))` to ensure they work on Android where the working directory might differ.
- Wrap `app.run()` in `if __name__ == '__main__':` block if not already (it seems it is not).

### Android Wrapper
#### [NEW] [main.py](file:///d:/final%20project/main.py)
- A Kivy application that:
    1. Starts the Flask server in a background thread.
    2. Opens a WebView (or system browser) pointing to `http://127.0.0.1:5000`.

#### [NEW] [buildozer.spec](file:///d:/final%20project/buildozer.spec)
- Configuration file for Buildozer.
- Defines requirements: `python3,flask,kivy,numpy,openssl`.
- Sets permissions: `INTERNET`.

#### [NEW] [ANDROID_GUIDE.md](file:///d:/final%20project/ANDROID_GUIDE.md)
- Instructions on how to build the APK using Buildozer (likely via WSL or Colab).

## Verification Plan

### Automated Tests
- We cannot run Android builds automatically here.
- We will verify `main.py` runs locally on Windows (it should start the server and open a window).

### Manual Verification
- Run `python main.py` and verify the app launches and the web interface is accessible.
