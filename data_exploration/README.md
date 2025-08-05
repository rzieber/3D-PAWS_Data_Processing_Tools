# Overview
The data exploration folder contains scripts which process CSV data for exploratory analysis of standard meteorological variables.
These scripts have been designed to work out of the box with any 3D-PAWS csv's downloaded via the CHORDS API.<br>
There exists the option to create some basic plots using the cleaned dataset. By including a folder into which plots are output, the script
will enable this functionality.<br>
<br>
Running `main.py` will produce the following results:
- Raw data is cleaned:
  - Duplicate timestamps eliminated
  - Out-of-order timestamps sorted (ascending)
  - Time gaps filled in with empty rows
- A report containing all data points removed during the cleaning process is generated 
- A CSV is generated of the cleaned/reformatted data set

**Assumptions:**

- Timestamp column must be named `time`
- Data is reported every minute
- Variables are using the standard shortnames: bt1, ht1, st1, mt1, hh1, sh1, bp1, wg, wd, rg
- Source and destination folders follow this convention:
  - ```data``` folder contains raw data to be qc'd
  - ```reportts``` folder will contain the output from the qc script
  - ```plots``` folder will contain the plots (if using) 

# Dependancies 
```bash
pip install -r requirements.txt
```

# Usage
```bash
python3 main.py path/to/raw/data/folder path/to/output/folder
```
Optionally:
```bash
python3 main.py path/to/raw/data/folder path/to/output/folder path/to/plots/folder
```
