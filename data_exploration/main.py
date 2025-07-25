import sys
import warnings
import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from data_exploration._fill_time_gaps import fill_empty_rows

def main():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=pd.errors.SettingWithCopyWarning)

        # Setup -------------------------------------------------------------------------------------------------------------

        #data = Path("/Users/rzieber/Documents/3D-PAWS/AQI_Comparison/data")   
        data = Path(sys.argv[1])
        # plots = Path("/Users/rzieber/Documents/3D-PAWS/AQI_Comparison/plots")
        #report = Path("/Users/rzieber/Documents/3D-PAWS/AQI_Comparison/reports")
        report = Path(sys.argv[2])

        # --------------------------------------------------------------------------------------------------------------------

        # get the folder names in data, store in list, convert to dataframes, store those in list
        csv_files = list(data.glob("*.csv"))  # get all CSV files
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

            # create report of all modified data and produce cleaned csv
            file_name = csv_files[i].name
            outliers.to_csv(report / f"{file_name[:len(file_name)-4]}_outliers.csv", index=False)
            gaps_filled.to_csv(report / f"{file_name[:len(file_name)-4]}_cleaned.csv", index=False)
            print(f"\tProcess completed.")


if __name__ == "__main__":
    main()
