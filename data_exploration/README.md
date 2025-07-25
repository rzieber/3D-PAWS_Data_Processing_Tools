# Overview
The data exploration folder contains scripts which process CSV data for exploratory analysis of standard meteorological variables.
These scripts have been designed to work out of the box with any 3D-PAWS csv's downloaded via the CHORDS API.<br>
<br>
Running `main.py` will produce the following results:

- Raw data will be cleaned:
  - Duplicate timestamps eliminated
  - Out-of-order timestamps sorted (ascending)
  - Time gaps filled in with empty rows
- A CSV is generated of all data points eliminated during the cleaning process
- A CSV is generated of the cleaned/reformatted data set

**Assumptions:**

- Timestamp column must be named `time`
- Data is reported every minute

# Dependancies 
```bash
pip install -r requirements.txt
```

# Usage
```bash
python3 main.py path/to/raw/data/folder path/to/output/folder
```
