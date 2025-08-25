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

        """
        NOTE: In progress -- return to this with a generalized approach after identifying similarities.

        Create a helper function to map all known shortnames to standard shortnames used moving forward.
        Use that helper to create a generalized exploratory analyis plotting function.
        """
        # if plots:
        #     print("Starting preliminary plot gen ---------------------------------------------")

        #     vars = {    # starting with standard shortname array for simplicity -- this will break for more obscure 3D-PAWS csv's!!!!!!!!!!!
        #         'temperature':  (['bt1', 'ht1', 'st1', 'mt1'],  '˚C'),
        #         'humidity':     (['hh1', 'sh1'],                '%'),
        #         'pressure':     (['bp1'],                       'hPa'),
        #         'wind':         (['ws', 'wd'],                  ('m/s', '˚')),
        #         'rain':         (['rg'],                        'mm'),
        #         'aqi':          (['pm1s10','pm1s25','pm1e10',
        #                           'pm1e25','pm1s100','pm1e100'],'ppm')
        #     }
        #     meta = [    # ignore metadata (maybe it's worth excluding this in the future maybe we care about battery charge idk)
        #         'bcs', 'bpc', 'cfr', 'css', 'hth'
        #     ]

        #     try:
        #         os.makedirs(plots / file_name, exist_ok=True)
        #         try:
        #             for var in vars.keys():
        #                 os.makedirs(plots / file_name / var, exist_ok=True)
        #         except Exception as e:
        #             print("Error creating the directory:", plots / var)
        #     except Exception as e:
        #         print("Could not create the directory:", plots / file_name)

        #     gaps_filled['year_month'] = gaps_filled['time'].dt.to_period('M')
        #     gaps_filled.set_index('time', inplace=True)

        #     # create a time-series plot for each column in the dataframe (this needs to become more general)
        #     for col in gaps_filled.columns:
        #         if col in meta or col in ['ws', 'wg', 'wd', 'wgd']: continue    # don't plot metadata for now, ignore wind

        #         key = next((k for k, v in vars.items() if col in v), None)
        #         if key is None: print(col)

        #         for year_month, grouped in gaps_filled.groupby('year_month'):   
        #             plt.figure(figsize=(12, 6))

        #             plt.plot(grouped.index, grouped[f'{col}'], marker='.', markersize=1, label=f"{col}")
                
        #             plt.title(f'{file_name} -- {col} for {year_month}')
        #             plt.xlabel('Date')
        #             plt.ylabel(f'{key} ({vars[key][1]})')
        #             plt.xticks(rotation=45)

        #             plt.legend()

        #             plt.grid(True)
        #             plt.tight_layout()
        #             plt.savefig(plots / file_name / var / f"{year_month}_time-series.png")
                    
        #             plt.clf()
        #             plt.close()

        #         # This is going to require more fine-tuning and ability to specify what to do with what,
        #         # but for now it's ok to just create time-series

        #         # proposed workflow:
        #         # you have two menu's of choices, select which variable and select the style of plot

        #         # temperature: time-series
        #         # humidity: time-series
        #         # pressure: time-series
        #         # wind: wind roses
        #         # precip: time-series accumulation

        #     print("Process completed ---------------------------------------------------------\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        main(
            Path("/Users/rzieber/Documents/3D-PAWS/Storm_Surge_Comparison/data"), 
            Path("/Users/rzieber/Documents/3D-PAWS/Storm_Surge_Comparison/report"),
            timedelta(minutes=15)
        )
    else:
        if len(sys.argv) == 4: main(Path(sys.argv[1]), Path(sys.argv[2]), timedelta(minutes=int(sys.argv[3])))
        if len(sys.argv) == 5: main(Path(sys.argv[1]), Path(sys.argv[2]), timedelta(minutes=int(sys.argv[3])), Path(sys.argv[4]))
