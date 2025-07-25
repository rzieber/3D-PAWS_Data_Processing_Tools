# Overview
The data exploration folder contains scripts which process CSV data for exploratory analysis of standard meteorological variables.
These scripts have been designed to work out of the box with any 3D-PAWS csv's downloaded via the CHORDS API.<br>
<br>
Running ```main.py``` will produce the following results:<br>
    - Raw data will be cleaned<br>
        * duplicate timestamps eliminated
        * out-of-order timestamps sorted (ascending)
        * time gaps filled in with empty rows
    - A csv is generated of all datapoints eliminated during the cleaning process<br>
    - A csv is generated of the cleaned/reformatted data set<br>

Assumptions:<br>
    - Timestamp column must be named 'time'<br>
    - Data is reported every minute

# Dependancies 
```bash
pip install -r requirements.txt
```

# Usage
```bash
python3 main.py path/to/raw/data/folder path/to/output/folder
```
