"""
The Joey TSV format, while beautiful to look at, has \t delimiters of variable length.
This script standardizes the TSV delimiter spacing so that it may be read into a pandas dataframe.
"""

lines = None
standardized_lines = []

with open("/path/to/data/folder/" + "filename.dat",\
                'r', encoding='utf-8', errors='replace') as file:
    lines = file.readlines()

for line in lines:
    next_line = line.split(' ')
    standardized_line = [x for x in next_line if x != '']

    for l in range(len(standardized_line)-1):
        standardized_lines.append(standardized_line[l])
        standardized_lines.append('\t')
    
    standardized_lines.append(standardized_line[-1])

with open('path/to/data/folder' + "filename.csv", \
                'w', encoding='utf-8', errors='replace') as file:
    file.writelines(standardized_lines)


# --------------------------------------------------------------------------------------------------------------------

import csv

"""
This is how to take a csv with standard tab separation and turn it into Joey's TSV format.
"""
# reformat tsv 
with open("/path/to/folder"+"filename.csv", 'r', newline='') as infile, \
        open("/path/to/folder"+"filename.dat", 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile, delimiter='\t')
    header_row = "year  mon  day  hour  min  temp  humidity  actual_pressure avg_wind_dir  avg_wind_speed\n"
    reformat = "{:>4.0f}  {:>3.0f}  {:>3.0f}  {:>4.0f}  {:>3.0f}  {:>4.0f}  {:>8.2f}  {:>15.2f}  {:>11.0f}  {:>14.2f}"
    next(reader) # skip header
    outfile.write(header_row)
    l = 1
    for row in reader:
        l += 1
        try:
            numeric_values = [float(v) if v else 0.0 for v in row]
            formatted_row = reformat.format(*numeric_values)
            writer.writerow(formatted_row.split('/t')) # you HAVE to split the reformatted row like this 
        except ValueError as v:
            zzzzzz = None

# # or it's like this? 
# with open(temp_file_path, 'r', newline='') as infile, \
#     open(output_file_path, 'w', newline='') as outfile:
#     reader = csv.reader(infile)
#     writer = csv.writer(outfile, delimiter='\t')
#     header_row = "year  mon  day  hour  min  temp  humidity  actual_pressure avg_wind_dir  avg_wind_speed\n"
#     outfile.write(header_row)
#     reformat = "{:>4}  {:>3}  {:>3}  {:>4}  {:>3}  {:>4}  {:>8}  {:>15}  {:>11}  {:>14}"
#     next(reader)  # Skip the header row
#     for row in reader:
#         try:
#             # Use the reformat string to align values and write to the file
#             formatted_row = reformat.format(*row)
#             outfile.write(formatted_row + '\n')
#         except ValueError as v:
#             pass  # Handle or log the error as needed

# os.remove(data_destination+file[:len(file)-23]+f"_{year_month}_TEMP.dat")