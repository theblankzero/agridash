# Android Build Guide

This guide explains how to compile your Flask application into an Android APK using Buildozer.

## Prerequisites

Buildozer requires a Linux environment. Since you are on Windows, you have two options:
1. **Google Colab** (Easiest, no local setup required)
2. **WSL (Windows Subsystem for Linux)** (Requires installing Ubuntu on Windows)

---

## Option 1: Google Colab (Recommended)

1. Upload the following files to your Google Drive or a GitHub repository:
    - `main.py`
    - `agri_dash.py`
    - `buildozer.spec`
    - `agridash.db` (if you want to include the existing database)
    - `model.h5` (optional, see note below)
    - `templates/` folder (if any, though this app uses `render_template_string`)

2. Open a new [Google Colab Notebook](https://colab.research.google.com/).

3. Run the following commands in a cell to install Buildozer:
    ```python
    !pip install buildozer cython==0.29.33
    !sudo apt-get install -y \
        python3-pip \
        build-essential \
        git \
        python3 \
        python3-dev \
        ffmpeg \
        libsdl2-dev \
        libsdl2-image-dev \
        libsdl2-mixer-dev \
        libsdl2-ttf-dev \
        libportmidi-dev \
        libswscale-dev \
        libavformat-dev \
        libavcodec-dev \
        zlib1g-dev
    !sudo apt-get install -y libgstreamer1.0 \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good
    !sudo apt-get install -y libltdl-dev
    ```

4. Upload your project files to the Colab runtime (drag and drop into the file explorer on the left).

5. Run the build command:
    ```python
    !buildozer android debug
    ```

6. Once finished (it takes 15-20 mins), download the `.apk` file from the `bin/` directory.

---

## Option 2: WSL (Windows Subsystem for Linux)

1. Install Ubuntu from the Microsoft Store.
2. Open the Ubuntu terminal.
3. Update packages:
    ```bash
    sudo apt update
    sudo apt upgrade
    ```
4. Install dependencies (same as above list).
5. Navigate to your project folder (your Windows drives are mounted at `/mnt/c/`):
    ```bash
    cd /mnt/d/final\ project/
    ```
6. Run Buildozer:
    ```bash
    buildozer android debug
    ```

## Important Notes

> [!WARNING]
> **TensorFlow Compatibility**: The `model.h5` file requires TensorFlow. We have disabled ML features on Android by default because full TensorFlow is difficult to bundle. If you need ML, you must use `tflite-runtime` and convert your model to `.tflite`.

> [!TIP]
> **Debugging**: If the app crashes on launch, connect your phone via USB and run `adb logcat -s python` to see the error logs.
