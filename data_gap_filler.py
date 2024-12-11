from pandas import Index, Timestamp
import pandas as pd
import np
from datetime import timedelta
import sys

"""
Helper function to fill_empty_rows() 
The number of columns in each station's csv varies. This function dynamically builds a new row to fill in missing timestamps regardless
of however many columns there might be. Missing rows should be built with empty cells (np.nan)
columns -- the df's column attribute
missing_timestamp -- the timestamp for the missing row
"""
def _build_empty_row(columns:Index, missing_timestamp:Timestamp) -> list:
    if not isinstance(columns, Index):
        raise TypeError(f"The build_empty_row() function expects 'columns' parameter to be of type <Index>, passed: {type(columns)}")
    if not isinstance(missing_timestamp, Timestamp):
        raise TypeError(f"The build_empty_row() function expects 'missing_timestamp' parameter to be of type <Timestamp>, passed: {type(missing_timestamp)}")

    next_row = [missing_timestamp]
    for col in columns:
        if col == 'date':
            continue

        next_row.append(np.nan)

    return next_row

"""
Create a list to merge with the reformatted dataframe that fills in data gaps with missing timestamps. 
Merges that list with the reformatted dataframe and returns it. 
reformatted_df -- the df to reformat with data gaps filled
time_delta -- the dataset's resolution (1-minute reporting period)
set_index -- specify whether you want the dataframe returned by fc'n to have the index set (default False)
"""
def fill_empty_rows(reformatted_df:pd.DataFrame, time_delta:timedelta, set_index:bool=False):
    if not isinstance(reformatted_df, pd.DataFrame):
        raise ValueError(f"The fill_empty_row() function expects the 'reformatted_df' parameter to be of type <pd.DataFrame>, received: {type(reformatted_df)}")
    if not isinstance(time_delta, timedelta):
        raise ValueError(f"The fill_empty_row() function expects the 'time_delta' parameter to be of type <timedelta>, received: {type(time_delta)}")
    if not isinstance(set_index, bool):
        raise ValueError(f"The fill_empty_row() function expects the 'set_index' parameter to be of type <bool>, received: {type(set_index)}")

    if 'date' not in reformatted_df.columns: reformatted_df.reset_index(inplace=True)

    blank_rows = [] # a list of lists

    for i in range(len(reformatted_df)-1):
        current_timestamp = reformatted_df['date'].iloc[i]
        next_timestamp = reformatted_df['date'].iloc[i+1]

        while next_timestamp - current_timestamp > time_delta:
            current_timestamp += time_delta
            new_row = _build_empty_row(reformatted_df.columns, current_timestamp)
            if new_row is not None:
                blank_rows.append(new_row)
            
    if blank_rows:
        blank_rows_df = pd.DataFrame(blank_rows, columns=reformatted_df.columns)
        reformatted_df = pd.concat([reformatted_df, blank_rows_df]).sort_values('date').reset_index(drop=True)

    if set_index: reformatted_df.set_index('date', inplace=True)

    return reformatted_df