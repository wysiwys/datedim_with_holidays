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
from datetime import date

from result import is_err, is_ok
from datedim_generate.generate import Holidays


def test_add_holidays():
    """
    Test that adding holidays works as intended
    """

    holidays = Holidays()

    # Error cases
    assert(is_err(holidays.country_holidays(['ABCDEFG'])))
    assert(is_err(holidays.country_holidays([''])))
    assert(is_err(holidays.financial_holidays(['HIJKLMNOP'])))

    # Valid country codes are ok
    assert(is_ok(holidays.country_holidays(['US'])))
    assert(is_ok(holidays.country_holidays(['UK'])))
    assert(is_ok(holidays.financial_holidays(['ECB'])))

    # The empty list is ok because no holidays need to be added
    assert(is_ok(holidays.country_holidays([])))

def test_is_holiday():
    """
    Test that combined-country holiday identification works correctly
    """
    h = Holidays()
    h.country_holidays(["US","DE"])

    assert(h.is_holiday(date(2024,12,25)))
    # The day after Christmas is a holiday in DE but not US collection
    assert(h.is_holiday(date(2024,12,26)))
    # The 4th of July is a holiday in US but not in DE collection
    assert(h.is_holiday(date(2024,7,4)))
    assert(not h.is_holiday(date(2024,12,29)))

def test_is_holiday_financial():
    """
    Test financial holiday combinations
    """

    h = Holidays()
    assert(is_ok(h.financial_holidays(["NYSE"])))
    assert(h.is_holiday(date(2024,5,27)))
    assert(not h.is_holiday(date(2024,5,1)))
    assert(is_ok(h.financial_holidays(["ECB"])))
    assert(h.is_holiday(date(2024,5,1)))
