# datedim_with_holidays
Generate the date dimension for a data warehouse, with a country-specific holidays flag added using python `holidays`.

## How to use

Before running the script, set up the python virtual environment:
```
python3 -m venv env && source env/bin/activate
python3 -m pip install -r requirements.txt
```
To generate the date dimension table, e.g. between Jan 1 and Dec 31 2022, in csv format, with a single boolean flag for US and BR holidays:
```
python3 generate.py -s 2022-01-01 -e 2022-12-31 -c US BR -o csv
```

## Info

Internally, the python script makes use of the `polars` package.

The schema of the date dimension table is based loosely on the DATE dimension in https://www.cs.umb.edu/~poneil/StarSchemaB.PDF, which is a standard date dimension table.

