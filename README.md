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

The generated file can then be uploaded into Snowflake via the drag-and-drop interface, or imported into another database of your choice.
 
For more information about usage, run:
```
datedim_generate -h
```

## Info

Internally, the python script makes use of the `polars` package.

The schema of the date dimension table is based loosely on the DATE dimension in https://www.cs.umb.edu/~poneil/StarSchemaB.PDF, which is a standard date dimension table.

## Schema

The following columns will always be generated:

| Column | Type | Description |
|--------|--------|--------|
| datekey | int | `YYYYMMDD` representation of date |
| date_raw | date | The raw date |
| dayofweek | text | The full name of the day of the week (e.g. `Monday`) |
| dayofweek_short | text | The three-letter abbreviation of the day of the week (e.g. `Mon`) |
| month | text | The full name of the month (e.g. `August`) |
| year | int | The year, e.g. `2021` |
| yearmonthnum | int |  `YYYYMM` representation of the date, e.g. `202406` |
| monthyear | text | The three-letter abbreviation of the month, plus the year, e.g. `Aug2024` |
| daynuminweek | int | The number of the day of week, where 1=Monday and 7=Sunday |
| daynuminmonth | int | The day number in the month (for February 2, 1995 this would be `2`) |
| daynuminyear | int | The day number in the year (for December 31, 2022 this would be `365` |
| monthnuminyear | int | The month number in the year |
| iso_year | int | The year of the date in the ISO week numbering (may differ from `year`) |
| iso_weeknuminyear | int | The week number in the ISO week numbering |
| is_last_day_in_week | boolean | Indicates that this date is the last in the week |
| is_last_day_in_month | boolean | Indicates that this date is the last in the month |
| is_holiday | boolean | Indicates that this date is a holiday in at least one of the provided calendars |
| is_weekday | boolean | Indicates that this date is a weekday |

Additionally, the following columns will be generated for each country, if the `--holiday_names_columns` argument is provided:

| Column | Type | Description |
|--------|--------|--------|
| is_holiday_\<COUNTRY\> | boolean | Indicates that this date is a holiday in the \<COUNTRY\> calendar. |
| holiday_name_\<COUNTRY> | text | The name of the holiday in the \<COUNTRY\> calendar, if available. |

This also applies for financial holidays (e.g. ECB).
