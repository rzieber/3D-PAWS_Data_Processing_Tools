import json
import numpy as np
import pandas as pd

"""
PARAMETERS
headers - column names to be used in CSV                                        <list>
measurements - all other data points besides "at"                               <np.ndarray>
column_order - [OPTIONAL] specify an order for columns in df/csv                <list>
filepath - [OPTIONAL] export path for csv of df, default is the empty string    <str>
null_value - [OPTIONAL] char to fill empty cells, default is the empty string   <str>

Constructs a dataframe using a list of header names, timestamps, and measurements. 
Option to specify a column order for the dataframe. Timestamp column will always be first.
Returns the dataframe. Optional feature to generate a CSV of the df at the specified filepath.
"""
def df_builder(headers:list, measurements:list, column_order:list=[], filepath:str='', fill_empty='') -> pd.DataFrame: 
    if not isinstance(headers, list):
        raise TypeError(f"The 'headers' parameter in csv_builder() should be of type <list>, passed: {type(headers)}")
    if not isinstance(measurements, list):
        raise TypeError(f"The 'measurements' parameter in csv_builder() should be of type <list>, passed: {type(measurements)}")
    if not isinstance(column_order, list):
        raise TypeError(f"The 'column_order' parameter in csv_builder() should be of type <list>, passed: {type(column_order)}")
    if not isinstance(filepath, str):
        raise TypeError(f"The 'filepath' parameter in csv_builder() should be of type <str>, passed: {type(filepath)}")
    if not measurements:
        raise ValueError("[ERROR]: No valid measurements found in JSON file.")

    data = [] 
    
    for i in range(len(measurements)):
        measurement_dict = {header: measurements[i].get(header, fill_empty) for header in headers} 
        data.append(measurement_dict)
    
    df = pd.DataFrame(data)

    if 'at' in df.columns and 'at' in headers: df.rename(columns={'at':'time'}, inplace=True)

    if 'time' in df.columns: 
        df['time'] = pd.to_datetime(df['time'])

        df = df[['time'] + [col for col in df.columns if col != 'time']] # timestamp column always comes first in column order
        if column_order: 
            column_order = [col for col in column_order if col not in {'at', 'time'}]
            ordered_cols = [col for col in column_order if col in df.columns]
            remaining_cols = [col for col in df.columns if col not in column_order]

            df = df[ordered_cols + remaining_cols]
 
    if filepath: df.to_csv(filepath, index=False)

    return df

# -------------------------------------------------------------------------------------------------------------------------


with open("/path/to/json.file", 'r', encoding='utf-8', errors='coerce') as file:
    # Data structures to hold JSON data stream
    measurements = []  # list of dictionaries  (e.g. {'t1': 25.3, 'uv1': 2, 'rh1': 92.7, 'sp1': 1007.43, 't2': 26.9, 'vis1': 260})
    headers = set()

    for l, line in enumerate(file, start=1):
        try:
            dictionary_data = json.loads(line)
            measurements.append(dictionary_data)
            headers.update(dictionary_data.keys())

        except json.JSONDecodeError as e:
            print("============================================================")
            print(f"[ERROR]: JSONDecodeError on line {l}: {e}")
            print("============================================================\n")
            continue
        
        l += 1
    
    headers = list({key for d in measurements for key in d.keys()})

    df = df_builder(headers, measurements)
