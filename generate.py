"""
Generates a date dimension table for a data warehouse.

For more details, please run `python3 generate.py -h`

"""
#pylint: disable=W0511,R0903,R0911,C0301
import argparse
from datetime import datetime

import calendar
import holidays
import polars
from polars.datatypes import UInt8, UInt16, UInt32, Int64
from result import Ok, Err, Result

class Holidays:
    """
    Represents the list of lists of user-provided holidays
    """

    holidays = []
    def country_holidays(self, countries: set[str]) -> Result[None,str]:
        """
        Generate the country holidays from list
        """

        try:
            for country in countries:
                country_holidays =  holidays.country_holidays(country)
                self.holidays.append(country_holidays)
        except NotImplementedError as e:
            return Err(e)

        return Ok(None)

    def financial_holidays(self, ids: set[str]) -> Result[None,str]:
        """
        Generate the financial holidays from list
        """

        try:
            for i in ids:
                financial_holidays = holidays.financial_holidays(i)
                self.holidays.append(financial_holidays)
        except NotImplementedError as e:
            return Err(e)

        return Ok(None)

    def is_holiday(self, date: datetime.date) -> bool:
        """
        Given a provided date, check if it is included
        in at least one of the holiday lists.
        """

        for entry in self.holidays:
            if entry.get(date) is not None:
                return True

        return False




class Arguments:
    """
    Class to represent the arguments provided by the user,
    used to configure the date dimension generator.
    """

    out_format = 'parquet'
    start_date = None
    end_date = None
    holidays = None

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
        holidays = Holidays()
        match holidays.country_holidays(args.country_holidays):
            case Err(e):
                return Err(f'Error processing country holidays: {e}')

        match holidays.financial_holidays(args.financial_holidays):
            case Err(e):
                return Err(f'Error processing financial holidays: {e}')


        self.holidays = holidays

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

        # TODO: own structure
        df = polars.DataFrame(
                {
                    "datekey": format_date(date_range,"%Y%m%d"),
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
                    # TODO: should this be iso?
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

                    "last_day_in_week": date_range.dt.weekday() == 7,
                    "last_day_in_month": date_range.map_elements(
                        lambda x: x.day == last_day_of_month(x),
                        return_dtype=bool),
                    #   gen
                    "holiday": date_range.map_elements(
                        self.args.holidays.is_holiday,
                        return_dtype=bool),

                    # 6 = Saturday, 7 = Sunday
                    "weekday": date_range.dt.weekday() < 6
                    }
                )
        return DataFrame(df)


def main(args: Arguments):
    """
    Summary of functionality:
    1. Set up the generator from the validated arguments
    2. Generate the dataframe
    3. Output the dataframe to file with the provided format
    """
    generator = DateDimensionGenerator(args)

    df = generator.generate()

    df.output(args.out_format)



if __name__ == "__main__":
    match Arguments().parse():
        case Ok(args):
            main(args)
        case Err(e):
            print(e)
