"""
This renaming script will homogenize file names on a local machine.
"""

import os

directory = r"C://path//to//local//data//"
old_format = r"TSMS03_2023_04_02.dat"
sensor_name = r"TSMS05_" # BEFORE RUNNING THIS SCRIPT -- comment out line 28 os.rename() to verify changes are accurate!!!!

# ------------------------------------------------------------------

files = [] # list of lists of filenames under each directory
for file in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, file)):
        files.append(file)

files = sorted(files)

i = 0
for filename in files:
    if ".dat" in filename and len(filename) == len(old_format): 
        print("To reformat:", filename)

        date = filename[7:11] + filename[12:14] + filename[15:17] # ensure this splicing matches that in old_format
        new_filename = sensor_name + date + ".dat"
        
        # os.rename(directory+filename, directory+new_filename) # ===== COMMENT ME OUT BEFORE MAKING CHANGES
        
        i += 1
        print("Reformatted:", new_filename)
        print()

print(f"Number of files reformatted: {i}")