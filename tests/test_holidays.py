import pytest

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

def test_is_holiday_2():

    h = Holidays()
    assert(is_ok(h.financial_holidays(["NYSE"])))
    assert(h.is_holiday(date(2024,5,27)))
    assert(not h.is_holiday(date(2024,5,1)))
    assert(is_ok(h.financial_holidays(["ECB"])))
    assert(h.is_holiday(date(2024,5,1)))
