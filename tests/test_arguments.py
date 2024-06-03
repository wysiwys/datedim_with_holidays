
"""
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
#pylint: disable=W0212
from datetime import datetime, date

from result import is_err, is_ok
from datedim_generate.generate import Arguments

def test_init_arguments_dates():
    """
    Tests that initializing the Arguments with correct dates succeeds,
    and that doing the same with incorrect dates fails.
    """
    arguments = Arguments()
    # Missing start or end date: should fail
    assert is_err(arguments._Arguments__process_arguments(start_date='2022-01-01'))
    assert is_err(arguments._Arguments__process_arguments(end_date='2022-01-01'))

    # Checking date range validity, with different
    assert is_ok(
        arguments._Arguments__process_arguments(start_date='2021-12-31',end_date='2022-01-01'))
    assert is_err(
        arguments._Arguments__process_arguments(start_date='2022-12-31',end_date='2022-01-01'))
    assert is_ok(
        arguments._Arguments__process_arguments(start_date='1234-12-31',end_date='3424-12-01'))

    # Checking argument types for date range
    assert is_ok(
        arguments._Arguments__process_arguments(start_date=date(2021,12,31),end_date='2022-01-01'))
    assert is_ok(
        arguments._Arguments__process_arguments(start_date=date(2021,12,31),
            end_date=datetime.strptime('2022-01-01','%Y-%m-%d')))
    assert is_err(
        arguments._Arguments__process_arguments(start_date=date(2022,12,31),end_date='2022-01-01'))
    assert is_ok(
        arguments._Arguments__process_arguments(start_date=date(2021,12,31),
            end_date=date(2025,1,1)))

    # Checking invalid date input
    assert is_err(arguments._Arguments__process_arguments(
        start_date='2022-15-31',end_date='2022-01-99'))
    assert is_err(arguments._Arguments__process_arguments(start_date='',end_date='2022-01-99'))
    assert is_err(arguments._Arguments__process_arguments(start_date='',end_date='HELLO\n'))

def test_init_arguments_holidays():
    """
    Tests success and failure paths for holidays list initialization
    """
    arguments = Arguments()

    # Try basic country holidays
    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='2022-01-01', country_holidays=['US','BR']))
    assert arguments.holidays.holidays['US'] is not None
    assert arguments.holidays.holidays['BR'] is not None

    # Try incorrect country codes
    assert is_err(arguments._Arguments__process_arguments(
       start_date='1901-01-01',end_date='2022-01-01', country_holidays=['US','ABC']))
    assert is_err(arguments._Arguments__process_arguments(
       start_date='1901-01-01',end_date='2022-01-01', country_holidays=['HELLO']))
    assert is_err(arguments._Arguments__process_arguments(
       start_date='1901-01-01',end_date='2022-01-01', country_holidays=['ALL']))

    # Check different names of same holiday
    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='2022-01-01', country_holidays=['CA']))
    assert arguments.holidays.holidays['CA'] is not None
    assert arguments.holidays.holidays['CA'].get(date(2022,12,25)) == 'Christmas Day'
    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='2022-01-01', country_holidays=['BR']))
    assert arguments.holidays.holidays['BR'].get(date(2022,12,25)) is not None
    assert arguments.holidays.holidays['BR'].get(date(2022,12,25)) != 'Christmas Day'

    assert arguments.use_holiday_names is False



    # Clear arguments
    arguments = Arguments()
    assert arguments.holidays is None

    # Check financial holidays
    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='2022-01-01', financial_holidays=['ECB','NYSE']))
    assert arguments.holidays.holidays['NYSE'] is not None
    assert'US' not in arguments.holidays.holidays

    # Try incorrect financial holiday codes
    assert is_err(arguments._Arguments__process_arguments(
       start_date='1901-01-01',end_date='2022-01-01', financial_holidays=['ECB','ABC']))
    assert is_err(arguments._Arguments__process_arguments(
       start_date='1901-01-01',end_date='2022-01-01', financial_holidays=['HELLO']))
    assert is_err(arguments._Arguments__process_arguments(
       start_date='1901-01-01',end_date='2022-01-01', financial_holidays=['ALL']))

    assert arguments.use_holiday_names is False


def test_use_holiday_names():
    """
    Tests the holiday_names_column argument for both success and failure paths
    """

    arguments = Arguments()

    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP'], holiday_names_columns=True
       ))

    assert arguments.use_holiday_names

    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP'], holiday_names_columns=False
       ))

    assert not arguments.use_holiday_names

    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP']
       ))

    assert not arguments.use_holiday_names

    assert is_err(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP'], holiday_names_columns="true"
       ))

def test_output_format():
    """
    Test that the output format is processed correctly
    """

    # Test csv format
    arguments = Arguments()

    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP'], out_format='csv'
       ))

    assert arguments.out_format == 'csv'

    # Test parquet format
    arguments = Arguments()

    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP'], out_format='parquet'
       ))

    assert arguments.out_format == 'parquet'

    # Test default format (parquet)
    arguments = Arguments()

    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP']
       ))

    assert arguments.out_format == 'parquet'

    # Test capitalization
    arguments = Arguments()

    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP'], out_format="PaRqUeT"
       ))

    assert arguments.out_format == 'parquet'

    # Test unsupported format
    arguments = Arguments()

    assert is_err(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP'], out_format="sql"
       ))
