"""
This renaming script will homogenize file names on a local machine.
"""

import os

directory = r"/Users/rzieber/Documents/3D-PAWS/Turkiye/output/station_TSMS05/"
old_format = r"TSMS03_2023_04_02.dat"
# DON'T FORGET TO CHANGE THE DATE!!!!!!!!
sensor_name = r"TSMS05_"
# Don't forget to comment out os.rename to print results before making any changes!

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

        date = filename[7:11] + filename[12:14] + filename[15:17]
        new_filename = sensor_name + date + ".dat"
        # Don't forget to comment out os.rename to print results before making any changes!
        os.rename(directory+filename, directory+new_filename)
        
        i += 1
        print("Reformatted:", new_filename)
        print()

print(f"Number of files reformatted: {i}")