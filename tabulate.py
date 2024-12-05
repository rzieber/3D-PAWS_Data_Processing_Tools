import pandas as pd
from tabulate import tabulate

# Set the options to display all columns and rows
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Example DataFrame
df = pd.DataFrame({
    'A': range(1, 101),
    'B': range(101, 201),
    'C': range(201, 301),
    'D': range(301, 401),
    'E': range(401, 501)
})

# Display the DataFrame
print(tabulate(df, headers='keys', tablefmt='pretty'))
