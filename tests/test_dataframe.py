

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

from result import is_ok
from datedim_generate.generate import Arguments, DateDimensionGenerator

def test_has_correct_holiday_columns():
    """
    Test that the correct holiday columns were generated
    """

    # Simple case
    arguments = Arguments()

    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP'], holiday_names_columns=True
       ))
    generator = DateDimensionGenerator(arguments)
    df = generator.generate()
    assert 'is_holiday_JP' in df.df.columns
    assert 'holiday_name_JP' in df.df.columns

    # Multiple countries
    arguments = Arguments()

    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP','KR'], holiday_names_columns=True
       ))
    generator = DateDimensionGenerator(arguments)
    df = generator.generate()
    assert 'is_holiday_JP' in df.df.columns
    assert 'holiday_name_JP' in df.df.columns
    assert 'is_holiday_KR' in df.df.columns
    assert 'holiday_name_KR' in df.df.columns
    assert 'is_holiday_US' not in df.df.columns
    assert 'holiday_name_US' not in df.df.columns

    # Multiple countries and financial holiday sets
    arguments = Arguments()

    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-01',end_date='1998-12-31',
       country_holidays=['JP','KR'],
       financial_holidays=['NYSE','ECB'],
       holiday_names_columns=True
       ))
    generator = DateDimensionGenerator(arguments)
    df = generator.generate()
    assert 'is_holiday_JP' in df.df.columns
    assert 'holiday_name_JP' in df.df.columns
    assert 'is_holiday_KR' in df.df.columns
    assert 'holiday_name_KR' in df.df.columns
    assert 'is_holiday_US' not in df.df.columns
    assert 'holiday_name_US' not in df.df.columns
    assert 'is_holiday_ECB' in df.df.columns
    assert 'holiday_name_ECB' in df.df.columns
    assert 'is_holiday_NYSE' in df.df.columns
    assert 'holiday_name_NYSE' in df.df.columns

def test_range_without_holidays():
    """
    Test that correct holiday columns are placed, even if no holidays exist in that range
    """

    arguments = Arguments()

    assert is_ok(arguments._Arguments__process_arguments(
       start_date='1992-01-02',end_date='1992-01-03',
       country_holidays=['JP'], holiday_names_columns=True
       ))
    generator = DateDimensionGenerator(arguments)
    df = generator.generate()
    assert 'is_holiday_JP' in df.df.columns
    assert 'holiday_name_JP' in df.df.columns
    assert len(df.df) == 2
    assert not df.df['is_holiday_JP'].any()
