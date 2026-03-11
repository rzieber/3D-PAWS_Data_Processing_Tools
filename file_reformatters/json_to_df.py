import json
import logging
import pandas as pd
from pathlib import Path
import argparse

"""
ARGUMENTS
    headers - column names to be used in CSV                                            <list>
    measurements - data points at each timestamp                                        <list>
    column_order - [OPTIONAL] specify an order for columns in df/csv, default is None   <list>
    filepath - [OPTIONAL] export path for csv of df, default is None                    <Path>
    null_value - [OPTIONAL] char to fill empty cells, default is None                   <str>
RAISES
    TypeError - if parameters do not match the type specified by the argument
    ValueError - if the 'measurements' argument contains no data
----------------------------------------------------------------------------------------------    
Constructs a dataframe using a list of header names and measurements from JSON file. 
Options:
    - Specify a column order for the dataframe. Timestamp column will always be first.
    - Generate a CSV of the dataframe at a specified filepath.
    - Specify what to populate empty cells in the dataframe/csv with.
Returns the dataframe. Optional feature to generate a CSV of the df at the specified filepath.
"""
def _df_builder(headers:list, measurements:list, column_order:list=None, filepath:Path=None, fill_empty=None) -> pd.DataFrame: 
    if not isinstance(headers, list):
        raise TypeError(f"[ERROR]: The 'headers' parameter in csv_builder() should be of type <list>, passed: {type(headers)}")
    if not isinstance(measurements, list):
        raise TypeError(f"[ERROR]: The 'measurements' parameter in csv_builder() should be of type <list>, passed: {type(measurements)}")
    if column_order is not None and not isinstance(column_order, list):
        raise TypeError(f"[ERROR]: The 'column_order' parameter in csv_builder() should be of type <list>, passed: {type(column_order)}")
    if filepath is not None and not isinstance(filepath, Path):
        raise TypeError(f"[ERROR]: The 'filepath' parameter in csv_builder() should be of type <Path>, passed: {type(filepath)}")
    if not measurements:
        raise ValueError("[ERROR]: No valid measurements found in JSON file.")
    
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting conversion from JSON to pandas DataFrame.")

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

    logging.info("Dataframe successfully created.")

    return df


def main(json_file:str, filepath:str=None, column_order:list=None, fill_empty=None) -> pd.DataFrame:
    logging.basicConfig(level=logging.INFO)

    json_file = Path(json_file)
    filepath = Path(filepath) if filepath is not None else None

    with open(json_file, 'r', encoding='utf-8', errors='replace') as file:
        measurements = [] 

        for l, line in enumerate(file, start=1):
            try:
                dictionary_data = json.loads(line)
                measurements.append(dictionary_data)

            except json.JSONDecodeError as e:
                logging.error(f"[ERROR]: JSONDecodeError on line {l}\n{e}")
                continue
        
        headers = list({key for d in measurements for key in d.keys()})

        return _df_builder(
            headers=headers, 
            measurements=measurements,
            column_order=column_order, 
            filepath=filepath,
            fill_empty=fill_empty
        )


def parse_args():
    parser = argparse.ArgumentParser(description="[TODO]")

    parser.add_argument("json_file", type=str, help="File path to the JSON file which is to be converted into a dataframe.")
    parser.add_argument("--filepath", type=str, default=None, help="Optional file path where a csv of the dataframe may be downloaded.")
    parser.add_argument("--column_order", type=str, default=None, help="Optional order to assign columns in the dataframe.")
    parser.add_argument("--fill_empty", default=None, help="Optional value to fill in empty cells in the dataframe.")

    args = parser.parse_args()

    if args.column_order is not None:
        args.column_order = args.column_order.split(',')

    if args.fill_empty is not None:
        try:
            args.fill_empty = eval(args.fill_empty)
        except:
            pass  # fallback to string if eval fails

    return args.json_file, args.filepath, args.column_order, args.fill_empty


if __name__ == "__main__": 
    main(*parse_args())
