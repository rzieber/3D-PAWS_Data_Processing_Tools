import sys
import json
import numpy as np
import pandas as pd

"""
PARAMETERS
headers - column names to be used in CSV                                        <list>
time - timestamps collected from the "at" key                                   <np.ndarray>
measurements - all other data points besides "at"                               <np.ndarray>
filepath - [OPTIONAL] export path for csv of df, default is the empty string    <str>
null_value - [OPTIONAL] char to fill empty cells, default is the empty string   <str>

Constructs a dataframe using a list of header names, timestamps, and measurements.
Returns the dataframe. Optional feature to generate a CSV of the df at the specified filepath.
"""
def df_builder(headers:list, measurements:list, column_order:list, filepath:str='', fill_empty='') -> pd.DataFrame: 
    if not isinstance(headers, list):
        raise TypeError(f"The 'headers' parameter in csv_builder() should be of type <list>, passed: {type(headers)}")
    if not isinstance(measurements, list):
        raise TypeError(f"The 'measurements' parameter in csv_builder() should be of type <list>, passed: {type(measurements)}")
    if not isinstance(column_order, list):
        raise TypeError(f"The 'column_order' parameter in csv_builder() should be of type <list>, passed: {type(column_order)}")
    if not isinstance(filepath, str):
        raise TypeError(f"The 'filepath' parameter in csv_builder() should be of type <str>, passed: {type(filepath)}")

    data = [] # list of timestamps, measurements, test val's, and headers (to turn into dataframe)
    
    for i in range(len(measurements)):

        measurement_dict = {header: measurements[i].get(header, fill_empty) for header in headers} 
        data.append(measurement_dict)
    
    df = pd.DataFrame(data)

    if 'at' in df.columns and 'at' in headers: df.rename(columns={'at':'time'}, inplace=True)
    if 'time' in df.columns: df['time'] = pd.to_datetime(df['time'])
    
    for col in column_order:
        if col not in headers: print(f"[ERROR]: {col} not in headers.")
    
    df = df[column_order]

    if filepath: df.to_csv(filepath, index=False)

    return df

# -------------------------------------------------------------------------------------------------------------------------


with open("/Users/rzieber/Documents/3D-PAWS/Turkiye/raw/3DPAWS/2022_Jan-2024/station_TSMS08/20221031.log", 'r', encoding='utf-8', errors='coerce') as file:
    l = 1 # file line number counter

    # Data structures to hold JSON data stream
    measurements = []  # list of dictionaries  (e.g. {'t1': 25.3, 'uv1': 2, 'rh1': 92.7, 'sp1': 1007.43, 't2': 26.9, 'vis1': 260})
    headers = set()

    for line in file:
        try:
            print(line)
            dictionary_data = json.loads(line) # a dictionary containing all the variables in each line in file
            print(dictionary_data)
            
            measurements.append(dictionary_data)

            headers.update(dictionary_data.keys())

        except json.JSONDecodeError as e:
            print("============================================================")
            print(f"[ERROR]: JSONDecodeError on line {l}: {e}")
            print("============================================================\n")
            continue
        
        l += 1
    
    headers = list(headers.keys())
    # filepath = "/where/you/want/the/csv/stored/"+"csv_filename.csv" # OPTIONAL

    df = df_builder(headers, measurements, ['your', 'col', 'order'])
    # optional 4th parameter - include a filepath where a csv of the dataframe should be stored
    #  e.g. df_builder(headers, time, measurements, filepath)
