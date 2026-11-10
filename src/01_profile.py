"""Step 1: profile raw KuaiRand-Pure files (read-only). Output: reports/01_profile.txt

What this script does (no data is changed):
  for every raw CSV it prints / logs
    - shape (rows, columns)
    - number of full-row duplicates (all columns identical)
    - columns that contain missing values, with counts
    - one summary row per column: dtype, number of distinct values, and min / max / mean for numeric columns
    - for text columns, the 8 most frequent values (incl. NaN)
The output is used to decide the cleaning rules in 02_clean.py (e.g. the -124 and "UNKNOWN" missing codes).
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]           # project root = folder above src/
RAW = ROOT / "data/raw/KuaiRand-Pure/data"           # raw CSVs (read-only)
OUT = ROOT / "reports/01_profile.txt"

lines = []
def log(s=""):
    """Print a line and keep it, so the same text ends up in the report file."""
    print(s)
    lines.append(str(s))

for f in sorted(RAW.glob("*.csv")):
    df = pd.read_csv(f)
    log(f"=== {f.name}  shape={df.shape}")
    # full-row duplicates: rows identical in EVERY column. 02_clean.py removes duplicates on a narrower
    # event key (user, video, time_ms), which also catches rows that differ only in the logging hour bucket.
    log(f"full-row duplicates: {df.duplicated().sum()}")
    na = df.isna().sum()
    log(f"columns with NA: {na[na > 0].to_dict()}")
    with pd.option_context("display.width", 250, "display.max_columns", None, "display.max_rows", None):
        # one row per column: dtype + number of distinct values ...
        summary = pd.DataFrame({"dtype": df.dtypes.astype(str), "nunique": df.nunique()})
        # ... plus min / max / mean for numeric columns (text columns get NaN here)
        num = df.select_dtypes("number")
        summary = summary.join(num.agg(["min", "max", "mean"]).T)
        log(summary.to_string())
    # most frequent values of text columns, to spot placeholder codes such as "UNKNOWN"
    for c in df.select_dtypes(include=["object", "string"]).columns:
        log(f"  [{c}] top values: {df[c].value_counts(dropna=False).head(8).to_dict()}")
    log()

OUT.write_text("\n".join(lines))
