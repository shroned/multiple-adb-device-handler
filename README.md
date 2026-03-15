# multiple-adb-device-handler
A Python-based GUI tool designed to streamline ADB command execution across multiple connected devices. It eliminates the need to manually copy-paste Device Serial Numbers (DSNs) by providing a selectable device list and a quick-action dashboard for common QA and development tasks.

# Multiple ADB Device Handler (ADB Tool Box)

## Overview
Working with multiple ADB devices can be time-consuming, especially when you have to repeatedly specify the DSN (`adb -s <DSN>`) for every command.This tool provides a graphical interface to automatically list connected devices and execute commands with a single click.

## Features
* **Automated Device Listing:** View all connected devices in a dropdown menu. 
* **Streamlined Commands:** Execute ADB commands without typing "adb" every time.
* **Predefined QA Tools:** One-click buttons for fetching Build Version, Settings Version, pulling databases, and more.
* **Media Capture:** Integrated buttons for screen recording, screenshots, and screencasting.
* **Log Management:** Easily start and stop log recording with custom filenames. 

## Prerequisites
Ensure you have Python 3 installed. You will need the `tkinter` library:
* **Windows/macOS:** `pip install tk`
* **Linux:** `sudo apt-get install python3-tk` 

## How to Use
1. Connect your Android devices (via USB or `adb connect <IP>`).
2. Run the script:
   ```bash
   python3 multiple_adb.py
