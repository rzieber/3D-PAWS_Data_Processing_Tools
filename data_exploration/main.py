import os
import sys
import warnings
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from data_exploration._fill_time_gaps import fill_empty_rows

def main(data=None, report=None, time_delta=timedelta(minutes=1), plots=None,):
    with warnings.catch_warnings():
        # warnings.simplefilter("ignore", category=pd.errors.SettingWithCopyWarning)
        # warnings.simplefilter("ignore", category=UserWarning)

        csv_files = list(data.glob("*.csv")) 

        for csv in csv_files:
            df = pd.read_csv(csv, low_memory=False, parse_dates=['time'])
            df['time'] = df['time'].dt.floor('min')

            print("Starting 3D-PAWS data formatting ------------------------------------------")

            file_name = csv.name[:len(csv.name)-4]
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
            gaps_filled = fill_empty_rows(cleaned, time_delta)    
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

if __name__ == "__main__":
    if len(sys.argv) < 3:
        main(
            Path("/Users/rzieber/Documents/3D-PAWS/Storm_Surge_Comparison/data"), 
            Path("/Users/rzieber/Documents/3D-PAWS/Storm_Surge_Comparison/report"),
            timedelta(minutes=6)
            #Path("/Users/rzieber/Documents/3D-PAWS/Storm_Surge_Comparison/plots")
        )
    else:
        if len(sys.argv) == 4: main(Path(sys.argv[1]), Path(sys.argv[2]), timedelta(minutes=int(sys.argv[3])))
        if len(sys.argv) == 5: main(Path(sys.argv[1]), Path(sys.argv[2]), timedelta(minutes=int(sys.argv[3])), Path(sys.argv[4]))
