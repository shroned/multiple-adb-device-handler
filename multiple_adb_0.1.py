import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import time
from tkinter import filedialog
import os

scrcpy_processes = {}
scrcpy_status_dict = {}
scrcpy_lock = threading.Lock()


# Function for starting scrcpy
def start_scrcpy():
    selected_device = device_var.get().split(" - ")[0]

    scrcpy_command = ['scrcpy', '-s', selected_device, '--max-size', '720']

    try:
        scrcpy_process = subprocess.Popen(scrcpy_command)

        scrcpy_processes[selected_device] = scrcpy_process

        screen_recording_status_dict[selected_device] = "Screencasting with scrcpy started"

        check_scrcpy_thread = threading.Thread(target=check_scrcpy_status, args=(selected_device,))
        check_scrcpy_thread.daemon = True
        check_scrcpy_thread.start()

    except subprocess.CalledProcessError as e:
        print("Error running scrcpy:", e)


# Function to check the status of scrcpy process
def check_scrcpy_status(selected_device):
    scrcpy_process = scrcpy_processes.get(selected_device)

    if scrcpy_process:
        scrcpy_process.wait()

        del scrcpy_processes[selected_device]

        screen_recording_status_dict[selected_device] = "Screencasting with scrcpy stopped"


def execute_comment_script():
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(parent_dir, "testrail.py")

    try:
        result = subprocess.run(['python3', script_path], capture_output=True, text=True)
        if result.returncode == 0:
            result_text.config(state=tk.NORMAL)
            result_text.insert(tk.END, f"Comment Generated\n\n{result.stdout}\n")
            result_text.config(state=tk.DISABLED)
        else:
            result_text.config(state=tk.NORMAL)
            result_text.insert(tk.END, f"Error executing script:\n{result.stderr}\n")
            result_text.config(state=tk.DISABLED)
    except Exception as e:
        result_text.config(state=tk.NORMAL)
        result_text.insert(tk.END, f"Exception occurred:\n{str(e)}\n")
        result_text.config(state=tk.DISABLED)


screen_recording_threads = {}
screen_recording_status_dict = {}
screen_recording_events = {}
screen_recording_lock = threading.Lock()


# Function to start screen recording
def start_screen_recording():
    selected_device = device_var.get().split(" - ")[0]
    screen_recording_status_dict[selected_device] = "Recording screen"

    with screen_recording_lock:
        if selected_device not in screen_recording_threads or not screen_recording_threads[selected_device].is_alive():
            screen_recording_events[selected_device] = threading.Event()
            screen_recording_threads[selected_device] = threading.Thread(target=record_screen_thread,
                                                                         args=(selected_device,))
            screen_recording_threads[selected_device].daemon = True
            screen_recording_threads[selected_device].start()


# Function to stop screen recording
def stop_screen_recording():
    selected_device = device_var.get().split(" - ")[0]

    with screen_recording_lock:
        if selected_device in screen_recording_threads and screen_recording_threads[selected_device].is_alive():
            screen_recording_events[selected_device].set()
            screen_recording_threads[selected_device].join()

            del screen_recording_threads[selected_device]
            del screen_recording_events[selected_device]


# Function to record screen in a separate thread
def record_screen_thread(selected_device):
    stop_event = screen_recording_events[selected_device]

    video_file_name = video_file_name_entry.get()
    if not video_file_name:
        video_file_name = "screen_record.mp4"
        screen_recording_status_dict[selected_device] = f"Recording video as screen_record.mp4"
    elif not video_file_name.lower().endswith(".mp4"):
        video_file_name += ".mp4"

    command = ['adb', '-s', selected_device, 'shell', 'screenrecord', f'/sdcard/{video_file_name}']

    try:
        process = subprocess.Popen(command)

        while not stop_event.is_set() and process.poll() is None:
            time.sleep(1)

        if process.poll() is None:
            process.terminate()

        process.wait()

    except subprocess.CalledProcessError as e:
        print("Error running screenrecord:", e)

    screen_recording_status_dict[selected_device] = "Screen recording stopped"


# Function to pull Recorded Video
def pull_video():
    selected_device = device_var.get().split(" - ")[0]
    video_file_name = video_file_name_entry.get()
    if not video_file_name:
        video_file_name = "screen_record.mp4"
    elif not video_file_name.lower().endswith(".mp4"):
        video_file_name += ".mp4"
    pull_command = ['adb', '-s', selected_device, 'pull', f'/sdcard/{video_file_name}', video_file_name]
    result = subprocess.run(pull_command, capture_output=True, text=True)
    if result.returncode == 0:
        result_text.config(state=tk.NORMAL)
        result_text.insert(tk.END, f"Video pulled from {selected_device} as {video_file_name}\n")
        result_text.config(state=tk.DISABLED)
    else:
        result_text.config(state=tk.NORMAL)
        result_text.insert(tk.END, f"Failed to pull the video. Error: {result.stderr}\n")
        result_text.config(state=tk.DISABLED)


# Function for installing apk
def install_apk():
    selected_device = device_var.get().split(" - ")[0]

    file_path = filedialog.askopenfilename(filetypes=[("APK files", "*.apk")])

    if file_path:
        command = ['adb', '-s', selected_device, 'install', file_path]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            result_text.config(state=tk.NORMAL)
            result_text.insert(tk.END, f"APK installed on {selected_device}: {file_path}\n")
            result_text.config(state=tk.DISABLED)
        else:
            result_text.config(state=tk.NORMAL)
            result_text.insert(tk.END, f"Failed to install the APK. Error: {result.stderr}\n")
            result_text.config(state=tk.DISABLED)


# Function to execute the 1st  ADB command
def execute_command_1():
    selected_device = device_var.get().split(" - ")[0]
    command_2 = ["shell", "getprop ro.build.version.release"]

    try:
        result = subprocess.check_output(['adb', '-s', selected_device] + command_2, stderr=subprocess.STDOUT).decode()

        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, result)
        result_text.config(state=tk.DISABLED)

    except subprocess.CalledProcessError as e:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Failed to execute command: {e.output.decode()}")
        result_text.config(state=tk.DISABLED)


# Function to execute the second ADB command
def execute_command_2():
    selected_device = device_var.get().split(" - ")[0]
    adb_command(selected_device, ["shell",
                                  "getprop ro.build.version.sdk"])  # Replace "command_2" with your desired command


# Function to execute the third ADB command
def execute_command_3():
    selected_device = device_var.get().split(" - ")[0]
    adb_command(selected_device, ["shell",
                                  "getprop ro.build.type"])

# Function to Input text
def input_text():
    text = text_entry.get()
    try:
        full_command = ['adb', 'shell', 'input', 'text', f'"{text}"']

        subprocess.run(full_command, check=True)

        result_text.config(state=tk.NORMAL)
        result_text.insert(tk.END, "Text input successful.\n")
        result_text.config(state=tk.DISABLED)
    except subprocess.CalledProcessError as e:
        result_text.config(state=tk.NORMAL)
        result_text.insert(tk.END, f"Error executing command: {e.output.decode()}\n")
        result_text.config(state=tk.DISABLED)


# list connected ADB devices with names
def list_connected_devices_with_names():
    try:
        devices_output = subprocess.check_output(['adb', 'devices', '-l']).decode()
        devices_info = [line.strip().split() for line in devices_output.split('\n')[1:] if line.strip()]
        devices = [(info[0], info[-2]) for info in devices_info]
        return devices
    except subprocess.CalledProcessError:
        return []


# execute an ADB command on a specific device
def adb_command(device_serial, command):
    try:
        result = subprocess.check_output(['adb', '-s', device_serial] + command, stderr=subprocess.STDOUT).decode()
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)  # clear existing content
        result_text.insert(tk.END, f"Command executed on {device_serial}: {' '.join(command)}\n\n{result}")
        result_text.config(state=tk.DISABLED)  # disable text editing
    except subprocess.CalledProcessError as e:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)  # clear existing content
        result_text.insert(tk.END,
                           f"Failed to execute command on {device_serial}: {' '.join(command)}\n{e.output.decode()}")
        result_text.config(state=tk.DISABLED)  # disable text editing


# refresh the list of connected devices
def refresh_devices():
    devices = list_connected_devices_with_names()
    device_combobox['values'] = [f"{device[0]} - {device[1]}" for device in devices]
    if devices:
        device_combobox.set(f"{devices[0][0]} - {devices[0][1]}")
    else:
        device_combobox.set("")


def check_connected_devices():
    while True:
        connected_devices = [device[0] for device in list_connected_devices_with_names()]
        disconnected_devices = [device for device in log_recording_status_dict.keys() if
                                device not in connected_devices]
        for disconnected_device in disconnected_devices:
            log_recording_status_dict[disconnected_device] = "Device disconnected, log recording stopped"
        time.sleep(5)


log_recording_threads = {}
log_recording_status_dict = {}
log_recording_lock = threading.Lock()
log_recording_events = {}


# Function to start log recording for a specific device
def start_log_recording():
    selected_device = device_var.get().split(" - ")[0]
    log_recording_status_dict[selected_device] = "Recording logs"

    with log_recording_lock:
        if selected_device not in log_recording_threads or not log_recording_threads[selected_device].is_alive():
            log_recording_events[selected_device] = threading.Event()
            log_recording_threads[selected_device] = threading.Thread(target=record_logs_thread,
                                                                      args=(selected_device,))
            log_recording_threads[selected_device].daemon = True
            log_recording_threads[selected_device].start()


# Function to stop log recording for a specific device
def stop_log_recording():
    selected_device = device_var.get().split(" - ")[0]

    with log_recording_lock:
        if selected_device in log_recording_threads and log_recording_threads[selected_device].is_alive():
            log_recording_events[selected_device].set()
            log_recording_threads[selected_device].join()

            del log_recording_threads[selected_device]
            del log_recording_events[selected_device]


# Function to record logs in a separate thread
def record_logs_thread(selected_device):
    stop_event = log_recording_events[selected_device]
    log_file_name_entry_value = log_file_name_entry.get().strip()
    log_file_name = log_file_name_entry_value + ".txt" if log_file_name_entry_value else "logcat_logs.txt"

    # Update status message only if no log file name is provided
    if not log_file_name_entry_value:
        log_recording_status_dict[selected_device] = f"Recording logs as logcat_logs.txt"

    logcat_command = ['adb', '-s', selected_device, 'logcat', '-v', 'time']

    try:
        with open(log_file_name, 'w') as log_file:
            process = subprocess.Popen(logcat_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(process.stdout.readline, b''):
                log_file.write(line.decode('utf-8'))
                if stop_event.is_set():
                    break
    except subprocess.CalledProcessError as e:
        print("Error running logcat:", e)

    log_recording_status_dict[selected_device] = "Log recording stopped"


# Function to clear the output console
def clear_output_console():
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.config(state=tk.DISABLED)


# Button to capture a screenshot
def capture_screenshot():
    selected_device = device_var.get().split(" - ")[0]
    file_name = file_name_entry.get()
    if file_name:
        command = ['adb', '-s', selected_device, 'shell', 'screencap', f'/sdcard/{file_name}.png']
        subprocess.run(command)
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Capturing screenshot on {selected_device} as {file_name}.png...\n")
        result_text.config(state=tk.DISABLED)
        # Schedule the pull_screenshot function after a delay of 1500 milliseconds
        root.after(1500, lambda: threading.Thread(target=pull_screenshot).start())


# Button to pull the screenshot
def pull_screenshot():
    selected_device = device_var.get().split(" - ")[0]
    file_name = file_name_entry.get()
    if file_name:
        pull_command = ['adb', '-s', selected_device, 'pull', f'/sdcard/{file_name}.png', file_name + ".png"]
        result = subprocess.run(pull_command, capture_output=True, text=True)
        if result.returncode == 0:
            result_text.config(state=tk.NORMAL)
            result_text.insert(tk.END, f"Screenshot pulled from {selected_device} as {file_name}.png\n")
            result_text.config(state=tk.DISABLED)
        else:
            result_text.config(state=tk.NORMAL)
            result_text.insert(tk.END, f"Failed to pull the screenshot. Error: {result.stderr}\n")
            result_text.config(state=tk.DISABLED)


root = tk.Tk()
root.title("Fire Toolbox")

devices = list_connected_devices_with_names()
log_recording_status = tk.StringVar()

if not devices:
    no_device_label = tk.Label(root,
                               text="No ADB devices found. Make sure your Android devices are connected and ADB is set up correctly.")
    no_device_label.pack(padx=100, pady=50)
else:
    instruction_label = tk.Label(root, text="Select a device and enter an ADB command ")
    instruction_label.pack(padx=100, pady=10)

    # selecting a device
    device_var = tk.StringVar()
    device_label = tk.Label(root, text="Select a device:")
    device_label.pack()

    device_frame = tk.Frame(root)
    device_frame.pack()

    device_combobox = ttk.Combobox(device_frame, textvariable=device_var,
                                   values=[f"{device[0]} - {device[1]}" for device in devices], width=35)
    device_combobox.pack(side=tk.LEFT, padx=(0, 10))
    device_combobox.set(f"{devices[0][0]} - {devices[0][1]}")

    refresh_button = tk.Button(device_frame, text="Refresh (For New Device)", command=refresh_devices)
    refresh_button.pack(side=tk.LEFT)

    # enter the ADB command
    command_label = tk.Label(root,
                             text="Enter the ADB command without 'adb' \n Example : Just enter 'shell getprop ro.build.version.release' instead of 'adb shell getprop ro.build.version.release'")
    command_label.pack()

    command_entry = tk.Entry(root, width=90)
    command_entry.pack(padx=100, pady=10)


    # execute the ADB command when the button is clicked
    def execute_command():
        selected_device = device_var.get().split(" - ")[0]
        adb_command(selected_device, command_entry.get().split())


    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # 1st set of buttons with frame and pack
    execute_button = tk.Button(button_frame, text="Execute Command", command=execute_command)
    clear_output_button = tk.Button(button_frame, text="Clear Console", command=clear_output_console)

    clear_output_button.pack(side=tk.LEFT, padx=(0, 20))
    execute_button.pack(side=tk.LEFT, padx=(0, 10))

    # Scrolled text window
    result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
    result_text.pack(padx=10, pady=10)
    result_text.config(state=tk.DISABLED)

    element_frame = tk.Frame(root)
    element_frame.pack(padx=100, pady=10)

    # Label for log file name
    log_file_name_label = tk.Label(element_frame, text="Log File Name:")
    log_file_name_label.pack(side=tk.LEFT, padx=10)

    # Entry field for log file name
    log_file_name_entry = tk.Entry(element_frame, width=40)
    log_file_name_entry.pack(side=tk.LEFT, padx=10)

    # Button to start log recording
    start_log_button = tk.Button(element_frame, text="Start Log Recording", command=start_log_recording)
    start_log_button.pack(side=tk.LEFT, padx=10)

    stop_log_button = tk.Button(element_frame, text="Stop Log Recording", command=stop_log_recording)
    stop_log_button.pack(side=tk.LEFT, padx=20, pady=10)

    log_status_label = tk.Label(root, text="")
    log_status_label.pack(padx=100, pady=10)


    # Function to update the log status label with status for all devices
    def update_log_status_label():
        log_status = "\n".join([f"{device}: {status}" for device, status in log_recording_status_dict.items()])
        log_status_label.config(text=log_status)
        root.after(1000, update_log_status_label)


    update_log_status_label()

    # Start the device checking thread
    check_device_thread = threading.Thread(target=check_connected_devices)
    check_device_thread.daemon = True
    check_device_thread.start()

    # Create a frame for the buttons
    command_button_frame = tk.Frame(root)
    command_button_frame.pack(side=tk.TOP, padx=10, pady=10)

    # First row of buttons
    execute_button_1 = tk.Button(command_button_frame, text="Android Version", command=execute_command_1)
    execute_button_2 = tk.Button(command_button_frame, text="API Level", command=execute_command_2)
    execute_button_3 = tk.Button(command_button_frame, text="Build Variant ", command=execute_command_3)

    execute_button_1.grid(row=0, column=0, padx=(0, 10), pady=5)
    execute_button_2.grid(row=0, column=1, padx=(0, 10), pady=5)
    execute_button_3.grid(row=0, column=2, padx=(0, 10), pady=5)

    install_apk_button = tk.Button(command_button_frame, text="Install APK", command=install_apk)
    install_apk_button.grid(row=0, column=8, padx=(0, 10), pady=5)

    # Button to start scrcpy screencasting
    start_scrcpy_button = tk.Button(command_button_frame, text="Start scrcpy Screencasting", command=start_scrcpy)
    start_scrcpy_button.grid(row=0, column=9, padx=(0, 10), pady=5)
    screencap_frame = tk.Frame(root)
    screencap_frame.pack(pady=10)

    # Entry field for file name
    file_name_label = tk.Label(screencap_frame, text="Enter Screenshot Name:")
    file_name_label.pack(side=tk.LEFT, pady=10)
    file_name_entry = tk.Entry(screencap_frame, width=40)
    file_name_entry.pack(side=tk.LEFT, padx=10, pady=10)

    capture_button = tk.Button(screencap_frame, text="Capture and Pull Screenshot ", command=capture_screenshot)
    capture_button.pack(side=tk.LEFT, padx=20, pady=10)

    # Entry field for video file name
    video_file_name_label = tk.Label(screencap_frame, text="Enter Video Name:")
    video_file_name_label.pack(side=tk.LEFT, pady=10)
    video_file_name_entry = tk.Entry(screencap_frame, width=40)
    video_file_name_entry.pack(side=tk.LEFT, padx=10, pady=10)

    start_screen_button = tk.Button(screencap_frame, text="Start Screen Recording", command=start_screen_recording)
    start_screen_button.pack(side=tk.LEFT, padx=5, pady=10)

    stop_screen_button = tk.Button(screencap_frame, text="Stop Screen Recording", command=stop_screen_recording)
    stop_screen_button.pack(side=tk.LEFT, padx=5, pady=10)

    pull_video_button = tk.Button(screencap_frame, text="Pull Video", command=pull_video)
    pull_video_button.pack(side=tk.LEFT, padx=5, pady=10)

    command_button_frame_2 = tk.Frame(root)
    command_button_frame_2.pack(side=tk.TOP, padx=10, pady=10)

    text_entry = ttk.Entry(command_button_frame, width=30)
    text_entry.grid(row=0, column=5, padx=(0, 10), pady=5)

    execute_button = ttk.Button(command_button_frame, text="Input Text", command=input_text)
    execute_button.grid(row=0, column=6, padx=(0, 10), pady=5)

    screen_recording_status_var = tk.StringVar()
    screen_recording_status_label = tk.Label(root, textvariable=screen_recording_status_var)
    screen_recording_status_label.pack(side=tk.TOP, padx=100, pady=10)

    # Status label for screencasting with scrcpy at the bottom
    scrcpy_status_var = tk.StringVar()
    scrcpy_status_label = tk.Label(root, textvariable=scrcpy_status_var)
    scrcpy_status_label.pack(side=tk.BOTTOM, padx=100, pady=10)


    # Function to update the screen recording status label
    def update_screen_recording_status_label():
        while True:
            status_text = "\n".join(
                [f"{device}: {status}" for device, status in screen_recording_status_dict.items()])
            screen_recording_status_var.set(status_text)
            root.update_idletasks()
            time.sleep(1)


    # Function to update the scrcpy status label
    def update_scrcpy_status_label():
        while True:
            status_text = "\n".join(
                [f"{device}: {status}" for device, status in scrcpy_status_dict.items()])
            scrcpy_status_var.set(status_text)
            root.update_idletasks()
            time.sleep(1)


    # Start updating status labels in separate threads
    update_screen_recording_status_thread = threading.Thread(target=update_screen_recording_status_label)
    update_screen_recording_status_thread.daemon = True
    update_screen_recording_status_thread.start()

    update_scrcpy_status_thread = threading.Thread(target=update_scrcpy_status_label)
    update_scrcpy_status_thread.daemon = True
    update_scrcpy_status_thread.start()

root.mainloop()