import re
import ast
import pandas as pd
from pathlib import Path

"""
Take observations stored in JSON-lines style daily files (.log) and convert them
to one CSV per instrument folder. Also supports .log files directly under the parent.

Usage:
    - Set `parent_origin` to the folder that may contain subfolders (one per instrument)
      and/or .log files directly.
    - Set `data_destination` to where you want the CSV(s).
    - Each instrument folder produces <instrument_name>.csv.
      Logs directly in the parent produce <parent_folder_name>.csv.

          
Expected folder structure for parsing:

parent_origin/                     # e.g., "sd-card/"
├── Instrument_A/                  # one subfolder per instrument
│   ├── 2023-08-01.log
│   ├── 2023-08-02.log
│   └── ...
├── Instrument_B/
│   ├── 2023-08-01.log
│   ├── 2023-08-02.log
│   └── ...
├── Instrument_C/
│   └── ...
├── some_top_level_file.log        # (optional) logs directly under parent
└── ...


Output written to data_destination:

├── Instrument_A.csv
├── Instrument_B.csv
├── Instrument_C.csv
└── parent_origin.csv              # only if top-level logs exist
"""

parent_origin = Path("path/to/data/folder")
data_destination = Path("path/to/output/folder")
data_destination.mkdir(parents=True, exist_ok=True)

def parse_line(s: str):
    s = s.strip()
    if not s:
        return None
    
    s = re.sub(r',\s*([}\]])', r'\1', s)    # remove dangling commas before closing } or ]
    try:
        obj = ast.literal_eval(s)           # tolerant of single quotes, numbers, etc.
        return dict(obj) if isinstance(obj, dict) else None
    except Exception:
        return None

def process_one_instrument(log_paths: list[Path], out_name: str, destination: Path):
    """Aggregate daily .log files into a single CSV for one instrument."""
    all_dfs = []
    headers: list[str] = []                 # order-preserving
    seen = set()

    for log in sorted(log_paths):
        print(f"Reading {log}")
        rows = []
        with open(log, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                rec = parse_line(line)
                if rec is None:
                    continue
                rows.append(rec)
                
                for k in rec.keys():        # extend headers in first-seen key order
                    if k not in seen:
                        headers.append(k)
                        seen.add(k)

        if not rows:
            continue

        df = pd.DataFrame(rows)
        
        df = df.reindex(columns=headers)    # align columns in first-seen order (keeps any missing as NaN)

        if 'at' in df.columns and 'time' not in df.columns:
            df['at'] = pd.to_datetime(df['at'], errors='coerce')
            df.rename(columns={'at': 'time'}, inplace=True)
        elif 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'], errors='coerce')

        all_dfs.append(df)

    if not all_dfs:
        print(f"No records for {out_name}; skipping.")
        return

    out_df = pd.concat(all_dfs, axis=0, ignore_index=True)

    
    if 'time' in out_df.columns:            # if 'time' column exists, sort by it
        out_df.sort_values(by='time', inplace=True)

    out_path = destination / f"{out_name}.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Wrote {len(out_df)} rows → {out_path}")

def main(parent: Path, destination: Path):
    # Collect instrument folders (dirs) and any .log files directly in parent.
    instrument_dirs = [p for p in parent.iterdir() if p.is_dir()]
    top_level_logs = list(parent.glob("*.log"))

    # 1) Process logs directly in the parent (if any) as a single bundle
    if top_level_logs:
        bundle_name = parent.name  # e.g., "sd-card"
        process_one_instrument(top_level_logs, bundle_name, destination)

    # 2) Process each instrument directory → one CSV per folder
    for inst_dir in sorted(instrument_dirs):
        # Find all .log files inside this instrument folder (and its subfolders if needed)
        # If each instrument folder may contain nested daily folders, rglob is appropriate:
        log_paths = list(inst_dir.rglob("*.log"))
        if not log_paths:
            print(f"No .log files found in {inst_dir}; skipping.")
            continue

        # Use the directory name as output name (safe, readable)
        out_name = inst_dir.name.replace(" ", "_")
        process_one_instrument(log_paths, out_name, destination)

if __name__ == "__main__":
    main(parent_origin, data_destination)
