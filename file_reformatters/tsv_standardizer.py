from pathlib import Path
import pandas as pd
import logging
import csv
import os

"""
ARGUMENTS
    input_file - the full file path to the TSV in column-aligned format                 <Path>
    output_file - the full file path where the standardized TSV file will be written    <Path>
RAISES
    TypeError - if 'input_file' or 'output_file' is not a Path object
    FileNotFoundError - if 'input_file' does not exist
    IsADirectoryError - if 'input_file' is a directory
    NotADirectoryError - if the directory of 'output_file' does not exist
    PermissionError - if there are insufficient permissions to read 'input_file',
                        or to write to 'output_file'
--------------------------------------------------------------------------------------------------
Many 3D-PAWS data files are formatted as column-aligned TSV's (coined "Joey's format").
This script reads in a column-aligned TSV and writes the contents to a standard TSV.
"""
def standardize_tsv(input_file:Path, output_file:Path) -> None:
    # Input validation
    if not isinstance(input_file, Path):
        raise TypeError(f"[ERROR]: Expected Path object for 'input_file', passed: {type(input_file)}")
    if not isinstance(output_file, Path):
        raise TypeError(f"[ERROR]: Expected Path object for 'output_file', passed: {type(output_file)}")
    if not input_file.exists():
        raise FileNotFoundError(f"[ERROR]: Input file not found: {input_file}")
    if not input_file.is_file():
        raise IsADirectoryError(f"[ERROR]: Input path is a directory, not a file: {input_file}")
    if not output_file.parent.exists():
        raise NotADirectoryError(f"[ERROR]: Output directory does not exist: {output_file.parent}")
    if not os.access(input_file, os.R_OK):
        raise PermissionError(f"[ERROR]: No read permission for input file: {input_file}")
    if not os.access(output_file.parent, os.W_OK):
        raise PermissionError(f"[ERROR]: No write permission for output directory: {output_file.parent}")
    
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Starting to process file {input_file.name}")

    # Read the input file and store contents
    lines = None
    standardized_lines = []

    try:
        with open(input_file, 'r', encoding='utf-8', errors='replace') as file:
            lines = file.readlines()

        # Process the contents of the input file
        for line in lines:
            next_line = line.split(' ')
            standardized_line = [x for x in next_line if x != '']

            standardized_lines.extend(element + '\t' for element in standardized_line[:-1])
            standardized_lines.append(standardized_line[-1])

        # Write the input file contents to standardized tsv format
        with open(output_file, 'w', encoding='utf-8', errors='replace') as file:
            file.writelines(standardized_lines)
        
        logging.info(f"Finished processing file {input_file.name}")
    
    except Exception as e:
        logging.error(f"[ERROR]: An error occurred while processing the file {input_file.name}\n{e}")

    return None


"""
ARGUMENTS
    input_file - the full file path to the TSV in column-aligned format                 <Path>
    output_file - the full file path where the standardized TSV file will be written    <Path>
    header_row - string with all the column names
RAISES
    TypeError - if 'input_file' or 'output_file' is not a Path object
    FileNotFoundError - if 'input_file' does not exist
    IsADirectoryError - if 'input_file' is a directory
    NotADirectoryError - if the directory of 'output_file' does not exist
    PermissionError - if there are insufficient permissions to read 'input_file',
                        or to write to 'output_file'
--------------------------------------------------------------------------------------------------
Accepts a standard csv file and converts it into a column-aligned TSV (aka Joey's format).
Requires a formatted header row, and a 'row_formatting' string that contains proper spacing,
as well as the name of the timestamp column if not already formatted. 
Joey's format breaks the timestamp column apart by year, month, day, hour, and minute. 
This script will do the same if the timestamp column isn't already in the year mon day hour min format.
"""
def align_columns(input_file:Path, output_file:Path, header_row:str, row_formatting:str, timestamp_col:str='') -> None:
    # Input validation
    if not isinstance(input_file, Path):
        raise TypeError(f"[ERROR]: Expected Path object for 'input_file', passed: {type(input_file)}")
    if not isinstance(output_file, Path):
        raise TypeError(f"[ERROR]: Expected Path object for 'output_file', passed: {type(output_file)}")
    if not isinstance(header_row, str):
        raise TypeError(f"[ERROR]: Expected string object for 'header_row', passed: {type(header_row)}")
    if not isinstance(row_formatting, str):
        raise TypeError(f"[ERROR]: Expected string object for 'row_formatting', passed: {type(row_formatting)}")
    if not isinstance(timestamp_col, str):
        raise TypeError(f"[ERROR]: Expected string object for 'timestamp_col', passed: {type(timestamp_col)}")
    if not input_file.exists():
        raise FileNotFoundError(f"[ERROR]: Input file not found: {input_file}")
    if not input_file.is_file():
        raise IsADirectoryError(f"[ERROR]: Input path is a directory, not a file: {input_file}")
    if not output_file.parent.exists():
        raise NotADirectoryError(f"[ERROR]: Output directory does not exist: {output_file.parent}")
    if not os.access(input_file, os.R_OK):
        raise PermissionError(f"[ERROR]: No read permission for input file: {input_file}")
    if not os.access(output_file.parent, os.W_OK):
        raise PermissionError(f"[ERROR]: No write permission for output directory: {output_file.parent}")
    
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Starting to process file {input_file.name}")

    df = pd.read_csv(input_file)

    # Pre-process the input file's timestamp column (if provided)
    if timestamp_col:
        df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')

        df['year'] = df[timestamp_col].dt.year
        df['mon'] = df[timestamp_col].dt.month
        df['day'] = df[timestamp_col].dt.day
        df['hour'] = df[timestamp_col].dt.hour
        df['min'] = df[timestamp_col].dt.minute

        df.drop(columns=[timestamp_col], inplace=True)

        print(df.columns)

        #input_file = input_file.parent+f"{input_file.name}_[TEMPORARY].csv"
    
        #df.to_csv(input_file)

    #with open(input_file, 'r', newline='') as infile, 
    with open(output_file, 'w', newline='') as outfile:
        #reader = csv.reader(infile)
        writer = csv.writer(outfile, delimiter='\t')

        #next(reader) # skip header
        outfile.write(header_row+'\n')
        
        for row_num, row in df.iterrows():
            #try:
            numeric_values = [float(v) if pd.notna(v) and not isinstance(v, str) else 0.0 for v in row]
            formatted_row = row_formatting.format(*numeric_values)
            writer.writerow(formatted_row.split('\t')) # you HAVE to split the reformatted row like this 
            
            # except ValueError as e:
            #     logging.warning(f"[WARNING]: Error processing {row_num+2}\n{e}")
            # except Exception as e:
            #     logging.error(f"[ERROR]: Unexpected error on row {row_num+2}\n{e}")
    
    logging.info(f"Finished processing file {input_file.name}")

    return None

# ----------------------------------------------------

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

def main():
    input = Path(r"C:\\Users\\Becky\\Downloads\\Konya_2022-02-04.csv")
    output = Path(r"C:\\Users\\Becky\\Downloads\\joeys_format_[TEST].csv")

    df = pd.read_csv(input)

    df.drop(columns=[
        'Station Number', 'Sunshine Duration','Mean Global Solar Radiation','Direct Solar Radiation Intensity',
        'Diffuse Solar Radiation Intensity','UVA Radiation Intensity','UVB Radiation Intensity','Mean Wind Speed at 10m',
        'Maximum Wind Speed at 10m','NRT Corrected Rainfall','PWS Current Rainfall','Maximum Wind Direction',
        'Maximum Wind Speed','Maximum Wind Time','Total Rainfall','year_month','year_month_day','Sea Level Pressure'
    ], inplace=True)

    input_2 = Path(str(input.parent)+'\\'+str(input.name[:len(input.name)-4])+'[TEMP].csv')
    print(input_2)

    df.to_csv(input_2, index=False)

    header_row = "year  mon  day  hour  min  temp  humidity  actual_pressure avg_wind_dir  avg_wind_speed"
    reformat = "{:>4.0f}  {:>3.0f}  {:>3.0f}  {:>4.0f}  {:>3.0f}  {:>4.0f}  {:>8.2f}  {:>15.2f}  {:>11.0f}  {:>14.2f}"

    align_columns(input_2, output, header_row, reformat)

if __name__ == "__main__": main()
