import os
import pandas as pd

complete_records = r"/Users/rzieber/Documents/3D-PAWS/Turkiye/reformatted/CSV_Format/TSMS/complete_record/"
monthly_records = r"/Users/rzieber/Documents/3D-PAWS/Turkiye/reformatted/CSV_Format/TSMS/monthly_records/"
daily_records = r"/Users/rzieber/Documents/3D-PAWS/Turkiye/reformatted/CSV_Format/TSMS/daily_records/"

file_names = [
    "Ankara_17130.csv", "Konya_17245.csv", "Adana_17351.csv"
]

for file in file_names:
    cr_filepath = os.path.join(complete_records, file)
    mr_filepath = os.path.join(monthly_records, file[:len(file)-10], file[:len(file)-10])
    dr_filepath = os.path.join(daily_records, file[:len(file)-10], file[:len(file)-10])

    df = pd.read_csv(
        cr_filepath, 
        header=0, 
        low_memory=False
    )

    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']])
    df.drop(
        ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Unnamed: 0'],
        axis=1,
        inplace=True
    )
    df['year_month'] = df['Date'].dt.to_period('M')
    df['year_month_day'] = df['Date'].dt.to_period('D')

    df.set_index('Date', inplace=True)

    for year_month, df_grouped in df.groupby('year_month'):
        df_grouped.to_csv(mr_filepath+f"_{year_month}.csv")
    
    for year_month_day, df_grouped in df.groupby('year_month_day'):
        df_grouped.to_csv(dr_filepath+f"_{year_month_day}.csv")
