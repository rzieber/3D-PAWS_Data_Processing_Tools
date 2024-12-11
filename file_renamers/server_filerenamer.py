"""
This renaming script will homogenize file names on a server accessible via ssh. Specifically, this script will homogonize the date format.
However, this same logic may be modified for other purposes. 
String splicing will have to be specified for your specific purposes with the 'date' parameter.

Use case: some files contain filenames like recordings_20240101.dat, while other have the format recordings_2024_01_01.dat

NOTE: Comment out line 61 and verify reformatting changes printed to the console before executing changes!

hostname -- the server (e.g. auto.comet.ucar.edu)
username -- your UCAR CIT username (same as email)
password -- your UCAR CIT password (same as email)
directory -- the folder path on the server (cd into folder and do pwd)
old_format -- the file naming convention to be altered (e.g. recordings_20230228.dat)
sensor_name_prefix -- whatever file naming convention there is before the date (e.g. recordings_)

date -- a spliced version from the OLD filename format, to be transformaed into the new file format
"""

import paramiko

# ------------------------------------------------------------------
# PARAMETERS

# SSH connection settings
hostname = "path.to.server"
username = "CIT username"
password = "CIT password"
port = 22  # Default SSH port

# file name structure
directory = r"~/path/to/folder/on/server/"
old_format = r"file-naming-convention-to-change.txt" 
sensor_name_prefix = "prefix_" # if you want to have some sort naming convention before the date
# BEFORE RUNNING THIS SCRIPT -- comment out line 61 ssh_client.exec_command to verify changes are accurate!!!!

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
            # ensure date splicing matches that in old_format

            new_filename = sensor_name_prefix + date + '.dat'

            # ssh_client.exec_command(f"mv {directory+filename} {directory+new_filename} ")
            
            i += 1
            print("Reformatted:", new_filename)
            print()

    print(f"Number of files reformatted: {i}")

finally:
    ssh_client.close()
