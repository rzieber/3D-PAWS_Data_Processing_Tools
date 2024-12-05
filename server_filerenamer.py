"""
This renaming script will homogenize file names on a server accessible via ssh.
"""

import os
from datetime import datetime
import paramiko

# SSH connection settings
hostname = "path.to.server"
username = "CIT username"
password = "CIT password"
port = 22  # Default SSH port

# ------------------------------------------------------------------

directory = r"~/path/to/folder/on/server/"
old_format = r"recordings_2023_02_28.dat"
sensor_name = r"recordings_" # BEFORE RUNNING THIS SCRIPT -- comment out line 49 ssh_client.exec_command to verify changes are accurate!!!!

# ------------------------------------------------------------------

# SSH connection setup
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh_client.connect(hostname, port=port, username=username, password=password)

    # Loop through each file in the directory
    stdin, stdout, stderr = ssh_client.exec_command(f"ls {directory}")
    files = stdout.read().decode().splitlines()

    i = 0

    for filename in files:
        if ".dat" in filename: 
            print("To reformat:", filename)

            date = filename[len(filename)-14:len(filename)-10] + filename[len(filename)-9:len(filename)-7] + filename[len(filename)-6:len(filename)-4]
            # date = filename[11:15] + filename[16:18] + filename[19:21] # ensure date splicing matches that in old_format
            i += 1

            # new_filename = sensor_name + date + '.dat'
            new_filename = filename[:len(filename)-14] + date + ".dat"

            # ssh_client.exec_command(f"mv {directory+filename} {directory+new_filename} ")
            
            print("Reformatted:", new_filename)
            print()

    print(f"Number of files reformatted: {i}")
finally:
    ssh_client.close()
