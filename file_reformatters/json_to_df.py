import json
import pandas as pd

"""
headers - column names to be used in CSV                                        <list>
measurements - data points at each timestamp                                    <list>
column_order - [OPTIONAL] specify an order for columns in df/csv                <list>
filepath - [OPTIONAL] export path for csv of df, default is the empty string    <str>
null_value - [OPTIONAL] char to fill empty cells, default is the empty string   <str>

Constructs a dataframe using a list of header names and measurements from JSON file. 
Options:
    - Specify a column order for the dataframe. Timestamp column will always be first.
    - Generate a CSV of the dataframe at a specified filepath.
    - Specify what to populate empty cells in the dataframe/csv with.
Returns the dataframe. Optional feature to generate a CSV of the df at the specified filepath.
"""
def df_builder(headers:list, measurements:list, column_order:list=[], filepath:str='', fill_empty='') -> pd.DataFrame: 
    # Input validation
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

    # Process measurements into a list of dictionaries
    data = [] 
    
    for i in range(len(measurements)):
        measurement_dict = {header: measurements[i].get(header, fill_empty) for header in headers} 
        data.append(measurement_dict)
    
    # Create dataframe and handle column ordering
    df = pd.DataFrame(data)

    if 'at' in df.columns and 'at' in headers: df.rename(columns={'at':'time'}, inplace=True)

    if 'time' in df.columns: 
        df['time'] = pd.to_datetime(df['time'])

        df = df[['time'] + [col for col in df.columns if col != 'time']] 
        if column_order: 
            column_order = [col for col in column_order if col not in {'at', 'time'}]
            ordered_cols = [col for col in column_order if col in df.columns]
            remaining_cols = [col for col in df.columns if col not in column_order]

            df = df[ordered_cols + remaining_cols]

    if filepath: df.to_csv(filepath, index=False)

    return df


def main():
    # Read JSON data from file and process it
    with open("/path/to/json.file", 'r', encoding='utf-8', errors='coerce') as file:
        measurements = [] 

        for l, line in enumerate(file, start=1):
            try:
                dictionary_data = json.loads(line)
                measurements.append(dictionary_data)

            except json.JSONDecodeError as e:
                print("============================================================")
                print(f"[ERROR]: JSONDecodeError on line {l}: {e}")
                print("============================================================\n")
                continue
            
            l += 1
        
        headers = list({key for d in measurements for key in d.keys()})

        # Create a dataframe from JSON data
        df = df_builder(headers, measurements)

if __name__ == "__main__": main()
