"""
Generates a date dimension table for a data warehouse.

For more details, please run `python3 generate.py -h`

--------------
MIT License

Copyright (c) 2024 wysiwys

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
#pylint: disable=W0511,R0903,R0911,C0301
import argparse
from datetime import datetime

import calendar
import holidays
import polars
from polars.datatypes import UInt8, UInt16, UInt32, Int64, Struct
from result import Ok, Err, Result

class Holidays:
    """
    Represents the list of lists of user-provided holidays
    """

    def __init__(self):
        """
        Initialize the struct with empty holidays
        """
        self.holidays = {}

    def country_holidays(self, countries: str | list[str]) -> Result[None,str]:
        """
        Generate the country holidays from list
        """

        if isinstance(countries,str):
            countries = [countries]

        try:
            for code in countries:
                self.holidays[code] =  holidays.country_holidays(code)
        except NotImplementedError as e:
            return Err(e)

        return Ok(None)

    def financial_holidays(self, ids: str | list[str]) -> Result[None,str]:
        """
        Generate the financial holidays from list
        """

        if isinstance(ids,str):
            ids = [ids]


        try:
            for code in ids:
                self.holidays[code] = holidays.financial_holidays(code)
        except NotImplementedError as e:
            return Err(e)

        return Ok(None)

    def is_empty(self) -> bool:
        """
        Returns True if any holidays lists are provided, else False
        """
        return len(self.holidays) == 0

    def is_holiday(self, date: datetime.date) -> bool:
        """
        Given a provided date, check if it is included
        in at least one of the holiday lists.
        """

        for entry in self.holidays.values():
            if entry.get(date) is not None:
                return True

        return False


    def get_holiday_names(self, date: datetime.date) -> dict[str,str]:
        """
        Given a provided date and holidays set code, get the names of all holidays
        """
        holidays_dict = {}

        # TODO: this could likely be made more efficient

        for holidays_id, holidays_set in self.holidays.items():
            if holidays_set is not None:
                if (holiday := holidays_set.get(date)) is not None:

                    # Configure holiday name entry
                    # Add the naming convention that will be used for the final column
                    holidays_dict["is_holiday_"+holidays_id] = True
                    holidays_dict["holiday_name_"+holidays_id] = holiday
                else:
                    holidays_dict["is_holiday_"+holidays_id] = False
                    holidays_dict["holiday_name_"+holidays_id] = None

        return holidays_dict



class Arguments:
    """
    Class to represent the arguments provided by the user,
    used to configure the date dimension generator.
    """

    out_format = 'parquet'
    start_date = None
    end_date = None
    holidays = None
    use_holiday_names = False

    def __init__(self):
        """
        Configure the parser, 
        including the description of the parser to be shown
        to the user when running with -h argument.
        """
        # TODO: limit the length of the input list

        #Provide general information and instructions.
        self.parser = argparse.ArgumentParser(
                description=\
                    """Generate date dimension for data warehouse, and optionally generate boolean holidays column.\nFor information on accepted country and financial holiday codes, please see https://python-holidays.readthedocs.io/en/latest/#available-countries""",
                formatter_class=argparse.RawTextHelpFormatter
                )

        # Configure the arguments for the parser.
        self.parser.add_argument('-s', '--start_date', help='Start date (as YYYY-MM-DD)')
        self.parser.add_argument('-e', '--end_date', help='End date (as YYYY-MM-DD)')
        self.parser.add_argument(
            '-c', '--country_holidays',
            nargs='+', default=[],
            help='Country holidays to use, as a space-separated list (e.g. US BR)')
        self.parser.add_argument(
            '-f', '--financial_holidays',
            nargs='+',default=[],
            help='Financial holidays to use, \
                    as a space-separated list (values can include ECB, IFEU, or XNYS)')
        self.parser.add_argument(
            '-o', '--out_format', default='parquet', 
            help='Format of output data: can be one of CSV, parquet (default is parquet)')
        self.parser.add_argument(
            '-n', '--holiday_names_columns', default=False,
            const=True, nargs='?',
            help='Whether to create a separate column for each country/financial holidays set, with names.\
                    \nFor each code, the following columns will be created:\
                    \n    \u2b29 is_holiday_[CODE] (boolean)\
                    \n    \u2b29 holiday_name_[CODE] (text)\
                    \nDefault is False.'
            )

    def parse(self):
        """
        Parse the arguments provided by the user.
        """

        args = self.parser.parse_args()

        # Handle the start and end dates
        # These must be provided as YYYY-MM-DD dates, and both dates both be provided.

        if args.start_date is None or args.end_date is None:
            return Err('Invalid configuration: must provide start and end date')
        try:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
        except ValueError as e:
            return Err(e)

        if start_date > end_date:
            return Err('Invalid configuration: Start date must be on or before end date')

        self.start_date, self.end_date = start_date, end_date


        # Handle the holidays
        user_holidays = Holidays()
        match user_holidays.country_holidays(args.country_holidays):
            case Err(e):
                return Err(f'Error processing country holidays: {e}')

        match user_holidays.financial_holidays(args.financial_holidays):
            case Err(e):
                return Err(f'Error processing financial holidays: {e}')


        self.holidays = user_holidays


        # Handle the holiday_names_columns argument
        # Check the case where names columns were requested but no holiday set ids provided
        if args.holiday_names_columns and self.holidays.is_empty():
            print("Warning: Ignoring holiday_names_columns argument since no holidays were provided")
        else:
            self.use_holiday_names = args.holiday_names_columns

        # Handle the output format
        # Allowed formats: parquet, csv
        match args.out_format.lower():
            case 'csv':
                self.out_format = 'csv'
            case 'parquet':
                self.out_format = 'parquet'
            case invalid:
                return Err(f'Invalid configuration: invalid output file format \'{invalid}\'. Options are: \'CSV\', \'parquet\'')


        return Ok(self)

# Helper functions for generating date metadata
def format_date(date_range: polars.Series, s: str) -> polars.Series:
    """
    Takes an arbitrary strftime format string, 
    and formats all of the elements of the provided series using it.
    """
    return date_range.map_elements(lambda x: x.strftime(s),return_dtype=str)

def last_day_of_month(d):
    """
    Provides the number of the last day of the month for a given date
    """
    return calendar.monthrange(d.year, d.month)[1]




class DataFrame:
    """
    Wrapper for polars.DataFrame
    """

    def __init__(self, df: polars.DataFrame):
        self.df = df

    def generate_holiday_columns(self, user_holidays: Holidays):
        """
        Generate the optional holiday name columns from the provided holidays
        """

        temp_column_name = "temp"

        # This is the expression that generates the column values
        # for each row of the final dataframe. The representation
        # for each row is the dictionary returned by
        # holidays.get_holiday_names(date).
        dict_column = polars.col('date_raw').map_elements(
                    user_holidays.get_holiday_names,return_dtype=Struct
                    ).alias(temp_column_name)

        self.df = self.df.with_columns(dict_column).unnest(temp_column_name)


    def output(self, out_format):
        """
        Given an output format (one of 'csv' or 'parquet'),
        output the wrapped dataframe to file.
        """

        match out_format:
            case 'csv':
                self.df.write_csv("datedimension.csv")
                print('Table saved to datedimension.csv')
            case 'parquet':
                self.df.write_parquet("datedimension.parquet")
                print('Table saved to datedimension.parquet')

class DateDimensionGenerator:
    """
    Class that generates the date dimension, given provided arguments
    """


    def __init__(self, args: Arguments):
        self.args = args


    def generate(self) -> DataFrame:
        """
        Generate the date dimension table as a dataframe
        """

        # First generate the date range
        date_range = polars.date_range(
                self.args.start_date, self.args.end_date, "1d", closed='both',
                eager=True
                ).alias("date")

        # Create the dataframe without the holiday names columns
        # TODO: make use of native polars api for strptime
        df = polars.DataFrame(
                {
                    "datekey": date_range.map_elements(
                        lambda x: int(x.strftime("%Y%m%d")),
                        return_dtype=UInt32),
                    "date_raw": date_range,
                    "dayofweek": format_date(date_range,"%A"),
                    "dayofweek_short": format_date(date_range,"%a"),
                    "month": format_date(date_range,"%B"),
                    "year": date_range.dt.year(),
                    "yearmonthnum": date_range.map_elements(
                        lambda x: int(x.strftime("%Y%m")),
                        return_dtype=Int64).cast(UInt32),
                    "monthyear": format_date(date_range,"%b%Y"),
                    "daynuminweek": date_range.dt.weekday().cast(UInt8),
                    "daynuminmonth": date_range.dt.day().cast(UInt8),
                    "daynuminyear": date_range.map_elements(
                        lambda x: x.timetuple().tm_yday,
                        return_dtype=Int64).cast(UInt16),
                    "monthnuminyear": date_range.dt.month().cast(UInt8),
                    "iso_year": date_range.map_elements(
                        lambda x: x.isocalendar().year,
                        return_dtype=Int64).cast(UInt16),
                    "iso_weeknuminyear": date_range.map_elements(
                        lambda x: x.isocalendar().week,
                        return_dtype=Int64).cast(UInt16),

                    # Boolean values below

                    "is_last_day_in_week": date_range.dt.weekday() == 7,
                    "is_last_day_in_month": date_range.map_elements(
                        lambda x: x.day == last_day_of_month(x),
                        return_dtype=bool),
                    #   gen
                    "is_holiday": date_range.map_elements(
                        self.args.holidays.is_holiday,
                        return_dtype=bool),

                    # 6 = Saturday, 7 = Sunday
                    "is_weekday": date_range.dt.weekday() < 6
                    }
                )

        df = DataFrame(df)

        if self.args.use_holiday_names:
            df.generate_holiday_columns(self.args.holidays)

        return df

def generate(args: Arguments):
    """
    Summary of functionality:
    1. Set up the generator from the validated arguments
    2. Generate the dataframe
    3. Output the dataframe to file with the provided format
    """
    generator = DateDimensionGenerator(args)

    df = generator.generate()

    df.output(args.out_format)


def main():
    """
    Handle the user-provided arguments,
    and pass them to the generator.
    """
    match Arguments().parse():
        case Ok(args):
            generate(args)
        case Err(e):
            print(e)

if __name__ == "__main__":
    main()
