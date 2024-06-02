# datedim_with_holidays
Generate the date dimension for a data warehouse, with country-specific holidays added using python `holidays`.

## Installation

Before running the script, set up the python virtual environment:
```
python3 -m venv env && source env/bin/activate
```
Then install using your package manager of choice:
```
python3 -m pip install .
```
OR
```
poetry install
```
## How to use
To generate the date dimension table, e.g. between Jan 1 and Dec 31 2022, in csv format, with a single boolean flag for US and BR holidays:
```
datedim_generate -s 2022-01-01 -e 2022-12-31 -c US BR -o csv
```

Alternatively, to generate the same date dimension table, but with separate columns for `is_holiday_US`, `holiday_name_US`, `is_holiday_BR`, and `holiday_name_BR`:
```
datedim_generate -s 2022-01-01 -e 2022-12-31 -c US BR -o csv --holiday_names_columns
```
 
For more information about usage, run:
```
datedim_generate -h
```

## Info

Internally, the python script makes use of the `polars` package.

The schema of the date dimension table is based loosely on the DATE dimension in https://www.cs.umb.edu/~poneil/StarSchemaB.PDF, which is a standard date dimension table.

