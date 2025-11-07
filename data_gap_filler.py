from pandas import Index, Timestamp
import pandas as pd
import numpy as np
from datetime import timedelta
from pathlib import Path
import os
import argparse

"""
Helper function to fill_empty_rows()
Builds a row to be merged with the dataframe for a missing timestamp.
Uses the dataframe's column order.

columns -- the df's column attribute
missing_timestamp -- the timestamp for the missing row
fill_empty -- specify what value should populate cells, np.nan by default [OPTIONAL] 
"""
def _build_empty_row(columns:Index, missing_timestamp:Timestamp, fill_empty=np.nan) -> list:
    if not isinstance(columns, Index):
        raise TypeError(f"The build_empty_row() function expects 'columns' parameter to be of type <Index>, passed: {type(columns)}")
    if not isinstance(missing_timestamp, Timestamp):
        raise TypeError(f"The build_empty_row() function expects 'missing_timestamp' parameter to be of type <Timestamp>, passed: {type(missing_timestamp)}")
    
    if pd.isna(missing_timestamp) or pd.isnull(missing_timestamp): return None

    next_row = []

    for col in columns:
        if col == 'time': next_row.append(missing_timestamp)
        else: next_row.append(fill_empty)

    return next_row


"""
Create a list to merge with the reformatted dataframe that fills in data gaps with missing timestamps. 
Merges that list with the reformatted dataframe, sorts by time, and returns it. 
REQUIREMENT: the timestamp column must be named 'time' ---------------------------------------------------

reformatted_df -- the df to reformat with data gaps filled
sampling_rate -- the dataset's resolution (1-minute reporting period)
set_index -- specify whether you want the dataframe returned by fc'n to have the index set (default False)
"""
def _fill_empty_rows(reformatted_df:pd.DataFrame, sampling_rate:int, set_index:bool=False):
    if not isinstance(reformatted_df, pd.DataFrame):
        raise ValueError(f"The fill_empty_row() function expects the 'reformatted_df' parameter to be of type <pd.DataFrame>, received: {type(reformatted_df)}")
    if not isinstance(sampling_rate, int):
        raise ValueError(f"The fill_empty_row() function expects the 'sampling_rate' parameter to be of type <int>, received: {type(sampling_rate)}")
    if not isinstance(set_index, bool):
        raise ValueError(f"The fill_empty_row() function expects the 'set_index' parameter to be of type <bool>, received: {type(set_index)}")

    nan_columns = reformatted_df.columns[reformatted_df.isna().all()]
    if not nan_columns.empty: 
        print("[WARNING]: fill_empty_rows() -- Empty columns:", nan_columns.tolist())

    if 'time' not in reformatted_df.columns: reformatted_df.reset_index(inplace=True)
    reformatted_df['time'] = pd.to_datetime(reformatted_df['time'])

    blank_rows = [] # a list of lists 
    td = timedelta(minutes=sampling_rate)

    to_filter = reformatted_df[reformatted_df['time'].isna()]
    reformatted_df = reformatted_df[~reformatted_df['time'].isna()]

    for i in range(len(reformatted_df)-1):
        current_timestamp = reformatted_df['time'].iloc[i].replace(second=0, microsecond=0)
        next_timestamp = reformatted_df['time'].iloc[i+1].replace(second=0, microsecond=0)

        while next_timestamp - current_timestamp > td:
            current_timestamp += td
            new_row = _build_empty_row(reformatted_df.columns, current_timestamp)
            if new_row is not None:
                blank_rows.append(new_row)

    if not blank_rows: return reformatted_df      
    else:
        blank_rows_df = pd.DataFrame(blank_rows, columns=reformatted_df.columns)
        reformatted_df = pd.concat([reformatted_df, blank_rows_df]).sort_values('time').reset_index(drop=True)

        reformatted_df.sort_values(by='time', inplace=True)

        pd.concat([to_filter, reformatted_df['time'].isna()])
        reformatted_df = reformatted_df[~reformatted_df['time'].isna()]
        if not to_filter.empty: print("[WARNING]: fill_empty_rows() -- Number of rows identified with invalid (NaT) timestamps:", len(to_filter['time'].tolist()))

        if set_index: reformatted_df.set_index('time', inplace=True)

        return reformatted_df



def main(data_directory:str, sampling_rate:int, data_destination:str):
    try:
        data_directory = Path(data_directory)
        data_destination = Path(data_destination)
    except Exception as e:
        print(f"[ERROR]: Could not convert the given folder path into a valid Path object: {e}")
    
    files = []
    for file in os.listdir(data_directory):
        if os.path.isfile(data_directory / file): 
            files.append(file)
        

    for file in files:
        df = pd.read_csv(data_directory / file)

        gaps_filled_df = _fill_empty_rows(df, sampling_rate)

        filename = file[:len(str(file))-4] + '_GAPS-FILLED.csv'

        gaps_filled_df.to_csv(data_destination / filename, index=False)



def parse_args() -> tuple[str, str]:
    parser = argparse.ArgumentParser(description="Given a folder path, fills in data gaps in csv's downloaded from a CHORDS portal.")
    
    parser.add_argument("data_directory",   type=str,   help="Directory path where CHORDS csv's are located.")
    parser.add_argument("sampling_rate",    type=int,   help="The instrument sampling rate (typically 1-minute).")
    parser.add_argument("data_destination", type=str,   help="Where the reformatted data should be stored.")
    
    args = parser.parse_args()

    return (args.data_path, args.portal)


if __name__ == "__main__":
    main(*parse_args())
