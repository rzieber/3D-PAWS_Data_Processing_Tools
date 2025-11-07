import os
import sys
import warnings
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
from pathlib import Path
import argparse

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from data_exploration._fill_time_gaps import fill_empty_rows

def main(data:str=None, report:str=None, sampling_rate:int=1, plots:str=None):
    try:
        data = Path(data) if data is not None else None
        report = Path(report) if report is not None else None
        sampling_rate = timedelta(minutes=sampling_rate)
        plots = Path(plots) if plots is not None else None
    except Exception as e:
        print(f"[ERROR]: could not parse argument -- {e}")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=pd.errors.SettingWithCopyWarning)
        warnings.simplefilter("ignore", category=UserWarning)

        csv_files = list(data.glob("*.csv")) 

        for csv in csv_files:
            df = pd.read_csv(csv, low_memory=False, parse_dates=['time'])
            df['time'] = df['time'].dt.floor('min')

            print("Starting 3D-PAWS data formatting ------------------------------------------")

            file_name = csv.stem
            print(f"\tProcessing dataframe for {file_name}.")

            # # TEMP FOR BARBADOS DATA
            # # merge matching timestamps into the same row
            # merged_df = (
            #     df.groupby('time', as_index=False)
            #     .agg(lambda x: x.dropna().iloc[0] if x.dropna().any() else None)
            # )

            # eliminate duplicate timestamps + log duplicates
            duplicates_mask = df.duplicated(                                    
                subset='time',
                keep='first'
            )
            duplicates = df[duplicates_mask]
            duplicates['removal_reason'] = 'Duplicate Timestamp'
            cleaned = df[~duplicates_mask]
            print("\t\tNumber of duplicate timestamps:", len(duplicates))

            # sort out-of-order timestamps + log those out of order
            out_of_order_mask = cleaned['time'] < cleaned['time'].shift(1)    
            out_of_order = cleaned[out_of_order_mask]
            out_of_order['removal_reason'] = 'Out Of Order Timestamp'
            cleaned.sort_values(by='time', inplace=True)
            print("\t\tNumber of out-of-order timestamps:", len(out_of_order))

            # fill in time gaps
            gaps_filled = fill_empty_rows(cleaned, sampling_rate)    
            print("\t\tData gaps (in minutes):", len(gaps_filled) - len(cleaned))
            print(f"\t\tNetwork uptime: {len(cleaned)/len(gaps_filled)}")

            # concat all the outlier dataframes together for report of modified data
            outliers = pd.concat(
                [duplicates, out_of_order],
                ignore_index=True
            )

            # create report of all modified data, produce cleaned csv, and statistical summary
            try:
                os.makedirs(report / file_name, exist_ok=True)
            except Exception as e:
                print("Could not create the directory:", report / file_name)

            outliers.to_csv(report / file_name / f"{file_name}_outliers.csv", index=False)
            gaps_filled.to_csv(report / file_name / f"{file_name}_cleaned.csv", index=False)
            gaps_filled.drop(columns=['time']).describe(include='all').round(2).to_csv(report / file_name / f"{file_name}_stats.csv")
        
        print("Process completed ---------------------------------------------------------\n")

        # if plots:
        #     print("Starting preliminary plot gen ---------------------------------------------")

        #     print(gaps_filled.columns)

        #     gaps_filled['week'] = gaps_filled['time'].dt.to_period('W')

        #     variable_mapper = {
                         
        #     }

        #     try:
        #         os.makedirs(plots / file_name, exist_ok=True)
        #         try:
        #             for var in vars.keys():
        #                 os.makedirs(plots / file_name / var, exist_ok=True)
        #         except Exception as e:
        #             print("Error creating the directory:", plots / var)
        #     except Exception as e:
        #         print("Could not create the directory:", plots / file_name)

        #     print("Process completed ---------------------------------------------------------\n")


def parse_args() -> tuple[str, str, timedelta, str]:
    parser = argparse.ArgumentParser(description="Performs basic data exploration for a set of CHORDS csv's.")

    parser.add_argument("data", type=Path, help="The directory which houses the CHORDS csv's.")
    parser.add_argument("report", type=Path, help="The directory to which a statistical report should be created for each CHORDS csv.")
    parser.add_argument("sampling_rate", type=int, help="The rate at which data is sampled for a 3D-PAWS instrument. Default: 1-minute")
    parser.add_argument("plots", type=str, help="The directory to which exploratory plots should be created for each CHORDS csv.")

    args = parser.parse_args()

    return (args.data, args.report, args.sampling_rate, args.plots)


if __name__ == "__main__":
    main(*parse_args())
