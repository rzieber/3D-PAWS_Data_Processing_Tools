import os
import sys
import pandas as pd
import numpy as np
from tabulate import tabulate
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from data_exploration._fill_time_gaps import fill_empty_rows

# Setup -------------------------------------------------------------------------------------------------------------

data = Path("/Users/rzieber/Documents/3D-PAWS/AQI_Comparison/data")   
plots = Path("/Users/rzieber/Documents/3D-PAWS/AQI_Comparison/plots")
report = Path("/Users/rzieber/Documents/3D-PAWS/AQI_Comparison/reports")

ajax = data / "UplandS_1min_S12.6.24_E5.12.25.csv"
kathyrn = data / "3D-PAWS_ID18_2024-12-06_2025-05-12.csv"
aqi = data / "3D-PAWS_ID16_2024-12-06_2025-05-12.csv"

ajax_df = pd.read_csv(
    ajax,
    header=2,
    low_memory=False,
    parse_dates=['UTC Date Time']
)
kathyrn_df = pd.read_csv(
    kathyrn,
    low_memory=False,
    parse_dates=['time']
)
aqi_df = pd.read_csv(
    aqi,
    low_memory=False,
    parse_dates=['time']
)

ajax_df.rename(columns={'UTC Date Time':'time'}, inplace=True)

# QC ----------------------------------------------------------------------------------------------------------------
 # drop columns we don't want to evaluate
ajax_df.drop(                                                          
    columns=['Local Date Time', 'Latitude', 'Longitude'],
    inplace=True
)
kathyrn_df.drop(
    columns=['sv1', 'si1', 'su1', 'bcs', 'bpc', 'cfr', 'css', 'hth', 'wd_compass_dir', 'wgd_compass_dir'], 
    inplace=True
)
aqi_df.drop(
    columns=['bcs', 'bpc', 'cfr', 'css', 'hth'],
    inplace=True
)

# eliminate duplicate timestamps + log duplicates
duplicates_mask = ajax_df.duplicated(                                    
    subset='time',
    keep='first'
)
ajax_duplicates = ajax_df[duplicates_mask]
ajax_duplicates['removal_reason'] = 'Duplicate Timestamp'
ajax_cleaned = ajax_df[~duplicates_mask]

duplicates_mask = kathyrn_df.duplicated(
    subset='time',
    keep='first'
)
kathryn_duplicates = kathyrn_df[duplicates_mask]
kathryn_duplicates['removal_reason'] = 'Duplicate Timestamp'
kathryn_cleaned = kathyrn_df[~duplicates_mask]

duplicates_mask = aqi_df.duplicated(
    subset='time',
    keep='first'
)
aqi_duplicates = aqi_df[duplicates_mask]
aqi_duplicates['removal_reason'] = 'Duplicate Timestamp'
aqi_cleaned = aqi_df[~duplicates_mask]

# sort out-of-order timestamps + log those out of order
out_of_order_mask = ajax_cleaned['time'] < ajax_cleaned['time'].shift(1)    
ajax_ooo = ajax_cleaned[out_of_order_mask]
ajax_ooo['removal_reason'] = 'Out Of Order Timestamp'
ajax_cleaned.sort_values(by='time', inplace=True)

out_of_order_mask = kathryn_cleaned['time'] < kathryn_cleaned['time'].shift(1)
kathryn_ooo = kathryn_cleaned[out_of_order_mask]
kathryn_ooo['removal_reason'] = 'Out Of Order Timestamp'
kathryn_cleaned.sort_values(by='time', inplace=True)

out_of_order_mask = aqi_cleaned['time'] < aqi_cleaned['time'].shift(1)
aqi_ooo = aqi_cleaned[out_of_order_mask]
aqi_ooo['removal_reason'] = 'Out Of Order Timestamp'
aqi_cleaned.sort_values(by='time', inplace=True)

# fill in time gaps
ajax_cleaned_gf = fill_empty_rows(ajax_cleaned, 1)                          
kathryn_cleaned_gf = fill_empty_rows(kathryn_cleaned, 1)
aqi_cleaned_gf = fill_empty_rows(aqi_cleaned, 1)

# concat all the outlier dataframes together for report of modified data
ajax_outliers = pd.concat(
    [ajax_duplicates, ajax_ooo],
    ignore_index=True
)
kathryn_outliers = pd.concat(
    [kathryn_duplicates, kathryn_ooo],
    ignore_index=True
)
aqi_outliers = pd.concat(
    [aqi_duplicates, aqi_ooo],
    ignore_index=True
)

# create report of all modified data
ajax_outliers.to_csv(report / "ajax_outliers.csv", index=False)
kathryn_outliers.to_csv(report / "kathryn_outliers.csv", index=False)
aqi_outliers.to_csv(report / "aqi_outliers.csv", index=False)

# print(tabulate(ajax_outliers, headers='keys', tablefmt='grid'))
# print(tabulate(kathryn_outliers, headers='keys', tablefmt='grid'))
# print(tabulate(aqi_outliers, headers='keys', tablefmt='grid'))

