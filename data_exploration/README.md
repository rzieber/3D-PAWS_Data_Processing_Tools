# Overview
The data exploration folder contains scripts which process CSV data for exploratory analysis of standard meteorological variables.
These scripts have been designed to work out of the box with any 3D-PAWS csv's downloaded via the CHORDS API.

Assumptions:<br>
    - Timestamp column must be named ```time```<br>
    - Data is reported every minute

# Usage
```bash
python3 main.py path/to/raw/data/folder path/to/output/folder
```

# Dependancies 
```bash
pip install -r requirements.txt
```
