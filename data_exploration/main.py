import sys
import warnings
import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from data_exploration._fill_time_gaps import fill_empty_rows

def main(data=None, report=None, plots=None):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=pd.errors.SettingWithCopyWarning)

        csv_files = list(data.glob("*.csv")) 
        dataframes = []

        for csv in csv_files:
            dataframes.append(  
                pd.read_csv(csv, low_memory=False, parse_dates=['time'])
            )

        print("Starting 3D-PAWS data formatting.")

        for i, df in enumerate(dataframes):
            print(f"\tProcessing dataframe number {i}.")

            # eliminate duplicate timestamps + log duplicates
            duplicates_mask = df.duplicated(                                    
                subset='time',
                keep='first'
            )
            duplicates = df[duplicates_mask]
            duplicates['removal_reason'] = 'Duplicate Timestamp'
            cleaned = df[~duplicates_mask]

            # sort out-of-order timestamps + log those out of order
            out_of_order_mask = cleaned['time'] < cleaned['time'].shift(1)    
            out_of_order = cleaned[out_of_order_mask]
            out_of_order['removal_reason'] = 'Out Of Order Timestamp'
            cleaned.sort_values(by='time', inplace=True)

            # fill in time gaps
            gaps_filled = fill_empty_rows(cleaned, 1)    

            # concat all the outlier dataframes together for report of modified data
            outliers = pd.concat(
                [duplicates, out_of_order],
                ignore_index=True
            )

            # create report of all modified data, produce cleaned csv, and statistical summary
            file_name = csv_files[i].name
            outliers.to_csv(report / f"{file_name[:len(file_name)-4]}_outliers.csv", index=False)
            gaps_filled.to_csv(report / f"{file_name[:len(file_name)-4]}_cleaned.csv", index=False)
            gaps_filled.drop(columns=['time']).describe(include='all').round(2).to_csv(report / f"{file_name[:len(file_name)-4]}_stats.csv")
            
            # vars = [
            #     'bt1', 'ht1', 'st1', 'mt1', # temperature
            #     'hh1', 'sh1',               # humidity
            #     'bp1',                      # pressure
            #     'ws', 'wd',                 # wind
            #     'rg'                        # precip
            # ]
            
            # rows = ['Variable', 'Mean', 'Mean Absolute Error', 'Root Mean ']
            # for v in vars:
            #     row = [v]

        
        print(f"Process completed.")

        # if sys.argv[3]:
        #     print("Starting preliminary plot gen.")



        #     print("Plot gen completed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        main(
            Path("/Users/rzieber/Documents/3D-PAWS/AQI_Comparison/data"), 
            Path("/Users/rzieber/Documents/3D-PAWS/AQI_Comparison/reports")
        )
    else:
        main(Path(sys.argv[1]), Path(sys.argv[2]))
    
