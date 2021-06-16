"""
gtime_unit.py

Unit testing for the calendars in the gtime module.py.
"""

import unittest

import gtime

class TestCalendarFirst(unittest.TestCase):
	"""Tests of the Calendar in the first year. (TestCase)"""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		self.calendar = gtime.Calendar(months)

	def test_day_of_month(self):
		"""Test first year of month day."""
		self.assertEqual(3, self.calendar.current_year[62]['day-of-month'])

	def test_month_name(self):
		"""Test first year of month name."""
		self.assertEqual('Third', self.calendar.current_year[62]['month-name'])

	def test_month_number(self):
		"""Test first year of month number."""
		self.assertEqual(3, self.calendar.current_year[62]['month-number'])

	def test_year_length(self):
		"""Test first year of year length."""
		self.assertEqual(90, self.calendar.current_year['year-length'])

class TestCalendarLater(unittest.TestCase):
	"""Tests of the Calendar in a later year. (TestCase)"""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		self.calendar = gtime.Calendar(months)
		self.calendar.set_year(7)

	def test_day_of_month(self):
		"""Test later year of month day."""
		self.assertEqual(3, self.calendar.current_year[62]['day-of-month'])

	def test_month_name(self):
		"""Test later year month name."""
		self.assertEqual('Third', self.calendar.current_year[62]['month-name'])

	def test_month_number(self):
		"""Test later year of month number."""
		self.assertEqual(3, self.calendar.current_year[62]['month-number'])

	def test_year_length(self):
		"""Test later year of year length."""
		self.assertEqual(90, self.calendar.current_year['year-length'])

class TestDevCalFirstDeviate(unittest.TestCase):
	"""Tests of the DeviationCalendar deviating the first time. (TestCase)"""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		deviation = gtime.Deviation('First', 30, lambda data: data['year'] % 3 == 0)
		self.calendar = gtime.DeviationCalendar(months, [deviation])
		self.calendar.set_year(3)

	def test_day_of_month(self):
		"""Test first instance of deviating month day."""
		self.assertEqual(30, self.calendar.current_year[30]['day-of-month'])

	def test_month_name(self):
		"""Test first instance of deviating month name."""
		self.assertEqual('First', self.calendar.current_year[30]['month-name'])

	def test_month_number(self):
		"""Test first instance of deviating month number."""
		self.assertEqual(1, self.calendar.current_year[30]['month-number'])

	def test_year_length(self):
		"""Test first instance of deviating year length."""
		self.assertEqual(91, self.calendar.current_year['year-length'])

class TestDevCalFirstMaintain(unittest.TestCase):
	"""Tests of the DeviationCalendar not deviating the first time. (TestCase)"""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		deviation = gtime.Deviation('First', 30, lambda data: data['year'] % 3 == 0)
		self.calendar = gtime.DeviationCalendar(months, [deviation])

	def test_day_of_month(self):
		"""Test first instance of not deviating month day."""
		self.assertEqual(1, self.calendar.current_year[30]['day-of-month'])

	def test_month_name(self):
		"""Test first instance of not deviating month name."""
		self.assertEqual('Second', self.calendar.current_year[30]['month-name'])

	def test_month_number(self):
		"""Test first instance of not deviating month number."""
		self.assertEqual(2, self.calendar.current_year[30]['month-number'])

	def test_year_length(self):
		"""Test first instance of not deviating year length."""
		self.assertEqual(90, self.calendar.current_year['year-length'])

class TestDevCalLaterDeviate(unittest.TestCase):
	"""Tests of the DeviationCalendar deviating at a later time. (TestCase)"""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		deviation = gtime.Deviation('First', 30, lambda data: data['year'] % 3 == 0)
		self.calendar = gtime.DeviationCalendar(months, [deviation])
		self.calendar.set_year(12)

	def test_day_of_month(self):
		"""Test later instance of deviating month day."""
		self.assertEqual(30, self.calendar.current_year[30]['day-of-month'])

	def test_month_name(self):
		"""Test later instance of deviating month name."""
		self.assertEqual('First', self.calendar.current_year[30]['month-name'])

	def test_month_number(self):
		"""Test later instance of deviating month number."""
		self.assertEqual(1, self.calendar.current_year[30]['month-number'])

	def test_year_length(self):
		"""Test later instance of deviating year length."""
		self.assertEqual(91, self.calendar.current_year['year-length'])

class TestDevCalLaterMaintain(unittest.TestCase):
	"""Tests of the DeviationCalendar not deviating at a later time. (TestCase)"""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		deviation = gtime.Deviation('First', 30, lambda data: data['year'] % 3 == 0)
		self.calendar = gtime.DeviationCalendar(months, [deviation])
		self.calendar.set_year(11)

	def test_day_of_month(self):
		"""Test later instance of not deviating month day."""
		self.assertEqual(1, self.calendar.current_year[30]['day-of-month'])

	def test_month_name(self):
		"""Test later instance of not deviating month name."""
		self.assertEqual('Second', self.calendar.current_year[30]['month-name'])

	def test_month_number(self):
		"""Test later instance of not deviating month number."""
		self.assertEqual(2, self.calendar.current_year[30]['month-number'])

	def test_year_length(self):
		"""Test later instance of not deviating year length."""
		self.assertEqual(90, self.calendar.current_year['year-length'])

class TestFracCalFirstOverage(unittest.TestCase):
	"""Tests of FractionalCalendar's first overage year. (TestCase)"""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		self.calendar = gtime.FractionalCalendar(90.334, months, 'First')
		self.calendar.set_year(2)

	def test_day_of_month(self):
		"""Test first instance of overage month day."""
		self.assertEqual(30, self.calendar.current_year[30]['day-of-month'])

	def test_month_name(self):
		"""Test first instance of overage month name."""
		self.assertEqual('First', self.calendar.current_year[30]['month-name'])

	def test_month_number(self):
		"""Test first instance of overage month number."""
		self.assertEqual(1, self.calendar.current_year[30]['month-number'])

	def test_year_length(self):
		"""Test first rounding up of fractional year."""
		self.assertEqual(91, self.calendar.current_year['year-length'])

class TestFracCalFirstYear(unittest.TestCase):
	"""Tests of FractionalCalendar's first year. (TestCase)"""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		self.calendar = gtime.FractionalCalendar(90.334, months, 'First')

	def test_day_of_month(self):
		"""Test first instance of no overage month day."""
		self.assertEqual(1, self.calendar.current_year[30]['day-of-month'])

	def test_month_name(self):
		"""Test first instance of no overage month name."""
		self.assertEqual('Second', self.calendar.current_year[30]['month-name'])

	def test_month_number(self):
		"""Test first instance of no overage month number."""
		self.assertEqual(2, self.calendar.current_year[30]['month-number'])

	def test_year_length(self):
		"""Test first rounding down of fractional year."""
		self.assertEqual(90, self.calendar.current_year['year-length'])

class TestFracCalLaterOverage(unittest.TestCase):
	"""Tests of a later FractionalCalendar overage year. (TestCase)"""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		self.calendar = gtime.FractionalCalendar(90.334, months, 'First')
		self.calendar.set_year(5)

	def test_day_of_month(self):
		"""Test a later instance of overage month day."""
		self.assertEqual(30, self.calendar.current_year[30]['day-of-month'])

	def test_month_name(self):
		"""Test a later instance of overage month name."""
		self.assertEqual('First', self.calendar.current_year[30]['month-name'])

	def test_month_number(self):
		"""Test a later instance of overage month number."""
		self.assertEqual(1, self.calendar.current_year[30]['month-number'])

	def test_year_length(self):
		"""Test a later rounding up of fractional year."""
		self.assertEqual(91, self.calendar.current_year['year-length'])

class TestFracCalLaterUnderage(unittest.TestCase):
	"""Tests of a FractionalCalendar later underage year. (TestCase)"""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		self.calendar = gtime.FractionalCalendar(90.334, months, 'First')
		self.calendar.set_year(6)

	def test_day_of_month(self):
		"""Test a later instance of no overage month day."""
		self.assertEqual(1, self.calendar.current_year[30]['day-of-month'])

	def test_month_name(self):
		"""Test a later instance of no overage month name."""
		self.assertEqual('Second', self.calendar.current_year[30]['month-name'])

	def test_month_number(self):
		"""Test a later instance of no overage month number."""
		self.assertEqual(2, self.calendar.current_year[30]['month-number'])

	def test_year_length(self):
		"""Test a later rounding down of fractional year."""
		self.assertEqual(90, self.calendar.current_year['year-length'])

class TestFracCycYear01(unittest.TestCase):
	"""Tests of a FractionalCycle in its first year."""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		moon = gtime.FractionalCycle('moon', ['Alpha', 'Beta', 'Gamma', 'Delta'], 25.31)
		self.calendar = gtime.Calendar(months, cycles = [moon])

	def test_first_end_cycle_day(self):
		"""Test the cycle day at the end of the first fractional period."""
		self.assertEqual(26, self.calendar.current_year[26]['moon-day'])

	def test_first_end_cycle_number(self):
		"""Test the cycle number at the end of the first fractional period."""
		self.assertEqual(1, self.calendar.current_year[26]['moon-number'])

	def test_first_end_frac_day(self):
		"""Test the fractional days at the end of the first fractional period."""
		self.assertAlmostEqual(50.62, self.calendar.current_year[26]['fractional-days'])

	def test_first_end_period_day(self):
		"""Test the period day at the end of the first fractional period."""
		self.assertEqual(1, self.calendar.current_year[26]['moon-period-day'])

	def test_first_end_period_name(self):
		"""Test the period name at the end of the first fractional period."""
		self.assertEqual('Beta', self.calendar.current_year[26]['moon-period'])

	def test_first_roundnot_cycle_day(self):
		"""Test the cycle day at the end of the first fractional period not rounded up."""
		self.assertEqual(77, self.calendar.current_year[77]['moon-day'])

	def test_first_roundnot_cycle_number(self):
		"""Test the cycle number at the end of the first fractional period not rounded up."""
		self.assertEqual(1, self.calendar.current_year[77]['moon-number'])

	def test_first_roundnot_frac_day(self):
		"""Test the fractional days at the end of the first fractional period not rounded up."""
		self.assertAlmostEqual(101.24, self.calendar.current_year[77]['fractional-days'])

	def test_first_roundnot_period_day(self):
		"""Test the period day at the end of the first fractional period not rounded up."""
		self.assertEqual(1, self.calendar.current_year[77]['moon-period-day'])

	def test_first_roundnot_period_name(self):
		"""Test the period name at the end of the first fractional period not rounded up."""
		self.assertEqual('Delta', self.calendar.current_year[77]['moon-period'])

	def test_first_roundup_cycle_day(self):
		"""Test the cycle day at the end of the first rounded-up fractional period."""
		self.assertEqual(52, self.calendar.current_year[52]['moon-day'])

	def test_first_roundup_cycle_number(self):
		"""Test the cycle number at the end of the first rounded-up fractional period."""
		self.assertEqual(1, self.calendar.current_year[52]['moon-number'])

	def test_first_roundup_frac_day(self):
		"""Test the fractional days at the end of the rounded-up first fractional period."""
		self.assertAlmostEqual(75.93, self.calendar.current_year[52]['fractional-days'])

	def test_first_roundup_period_day(self):
		"""Test the period day at the end of the first rounded-up fractional period."""
		self.assertEqual(1, self.calendar.current_year[52]['moon-period-day'])

	def test_first_roundup_period_name(self):
		"""Test the period name at the end of the first rounded-up fractional period."""
		self.assertEqual('Gamma', self.calendar.current_year[52]['moon-period'])

class TestFracCycYear02(unittest.TestCase):
	"""Tests of a FractionalCycle in its second year."""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		moon = gtime.FractionalCycle('moon', ['Alpha', 'Beta', 'Gamma', 'Delta'], 25.31)
		self.calendar = gtime.Calendar(months, cycles = [moon])
		self.calendar.set_year(2)

	def test_first_day_cycle_day(self):
		"""Test the cycle day on the first day of the year."""
		self.assertEqual(91, self.calendar.current_year[1]['moon-day'])

	def test_first_day_cycle_number(self):
		"""Test the cycle number on the first day of the year."""
		self.assertEqual(1, self.calendar.current_year[1]['moon-number'])

	def test_first_day_frac_day(self):
		"""Test the fractional days on the first day of the year."""
		self.assertAlmostEqual(101.24, self.calendar.current_year[1]['fractional-days'])

	def test_first_day_period_day(self):
		"""Test the period day on the first day of the year."""
		self.assertEqual(15, self.calendar.current_year[1]['moon-period-day'])

	def test_first_day_period_name(self):
		"""Test the period name on the first day of the year."""
		self.assertEqual('Delta', self.calendar.current_year[1]['moon-period'])

	def test_reset_cycle_day(self):
		"""Test the cycle day on the first day of the year."""
		self.assertEqual(1, self.calendar.current_year[12]['moon-day'])

	def test_reset_cycle_number(self):
		"""Test the cycle number on the first day of the year."""
		self.assertEqual(2, self.calendar.current_year[12]['moon-number'])

	def test_reset_frac_day(self):
		"""Test the fractional days on the first day of the year."""
		self.assertAlmostEqual(25.55, self.calendar.current_year[12]['fractional-days'])

	def test_reset_period_day(self):
		"""Test the period day on the first day of the year."""
		self.assertEqual(1, self.calendar.current_year[12]['moon-period-day'])

	def test_reset_period_name(self):
		"""Test the period name on the first day of the year."""
		self.assertEqual('Alpha', self.calendar.current_year[12]['moon-period'])

class TestFracCycYear03(unittest.TestCase):
	"""Tests of a FractionalCycle in its third year."""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		moon = gtime.FractionalCycle('moon', ['Alpha', 'Beta', 'Gamma', 'Delta'], 25.31)
		self.calendar = gtime.Calendar(months, cycles = [moon])
		self.calendar.set_year(3)

	def test_first_day_cycle_day(self):
		"""Test the cycle day on the first day of the year."""
		self.assertEqual(80, self.calendar.current_year[1]['moon-day'])

	def test_first_day_cycle_number(self):
		"""Test the cycle number on the first day of the year."""
		self.assertEqual(2, self.calendar.current_year[1]['moon-number'])

	def test_first_day_frac_day(self):
		"""Test the fractional days on the first day of the year."""
		self.assertAlmostEqual(101.48, self.calendar.current_year[1]['fractional-days'])

	def test_first_day_period_day(self):
		"""Test the period day on the first day of the year."""
		self.assertEqual(4, self.calendar.current_year[1]['moon-period-day'])

	def test_first_day_period_name(self):
		"""Test the period name on the first day of the year."""
		self.assertEqual('Delta', self.calendar.current_year[1]['moon-period'])

	def test_reset_cycle_day(self):
		"""Test the cycle day on the first day of the next cycle."""
		self.assertEqual(1, self.calendar.current_year[23]['moon-day'])

	def test_reset_cycle_number(self):
		"""Test the cycle number on the first day of the next cycle."""
		self.assertEqual(3, self.calendar.current_year[23]['moon-number'])

	def test_reset_frac_day(self):
		"""Test the fractional days on the first day of the next cycle."""
		self.assertAlmostEqual(25.79, self.calendar.current_year[23]['fractional-days'])

	def test_reset_period_day(self):
		"""Test the period day on the first day of the next cycle."""
		self.assertEqual(1, self.calendar.current_year[23]['moon-period-day'])

	def test_reset_period_name(self):
		"""Test the period name on the first day of the next cycle."""
		self.assertEqual('Alpha', self.calendar.current_year[23]['moon-period'])

class TestStaticCycYear01(unittest.TestCase):
	"""Test of a StaticCycle in its first year."""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		week = gtime.StaticCycle('weekday', {day: 1 for day in days})
		self.calendar = gtime.Calendar(months, cycles = [week])

	def test_first_day_cycle_day(self):
		"""Test the cycle day on the first day of the year."""
		self.assertEqual(1, self.calendar.current_year[1]['weekday-day'])

	def test_first_day_cycle_number(self):
		"""Test the cycle number on the first day of the year."""
		self.assertEqual(1, self.calendar.current_year[1]['weekday-number'])

	def test_first_day_period_day(self):
		"""Test the period day on the first day of the year."""
		self.assertEqual(1, self.calendar.current_year[1]['weekday-period-day'])

	def test_first_day_period_name(self):
		"""Test the period name in the middle of the year."""
		self.assertEqual('Monday', self.calendar.current_year[1]['weekday-period'])

	def test_mid_year_cycle_day(self):
		"""Test the cycle day in the middle of the year."""
		self.assertEqual(3, self.calendar.current_year[45]['weekday-day'])

	def test_mid_year_cycle_number(self):
		"""Test the cycle number in the middle of the year."""
		self.assertEqual(7, self.calendar.current_year[45]['weekday-number'])

	def test_mid_year_period_day(self):
		"""Test the period day in the middle of the year."""
		self.assertEqual(1, self.calendar.current_year[45]['weekday-period-day'])

	def test_mid_year_period_name(self):
		"""Test the period name in the middle of the year."""
		self.assertEqual('Wednesday', self.calendar.current_year[45]['weekday-period'])

class TestStaticCycYear02(unittest.TestCase):
	"""Test of a StaticCycle in its second year."""

	def setUp(self):
		months = {'First': 29, 'Second': 30, 'Third': 31}
		days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		week = gtime.StaticCycle('weekday', {day: 1 for day in days})
		self.calendar = gtime.Calendar(months, cycles = [week])
		self.calendar.set_year(2)

	def test_first_day_cycle_day(self):
		"""Test the cycle day on the first day of the year."""
		self.assertEqual(7, self.calendar.current_year[1]['weekday-day'])

	def test_first_day_cycle_number(self):
		"""Test the cycle number on the first day of the year."""
		self.assertEqual(13, self.calendar.current_year[1]['weekday-number'])

	def test_first_day_period_day(self):
		"""Test the period day on the first day of the year."""
		self.assertEqual(1, self.calendar.current_year[1]['weekday-period-day'])

	def test_first_day_period_name(self):
		"""Test the period name in the middle of the year."""
		self.assertEqual('Sunday', self.calendar.current_year[1]['weekday-period'])

	def test_mid_year_cycle_day(self):
		"""Test the cycle day in the middle of the year."""
		self.assertEqual(2, self.calendar.current_year[45]['weekday-day'])

	def test_mid_year_cycle_number(self):
		"""Test the cycle number in the middle of the year."""
		self.assertEqual(20, self.calendar.current_year[45]['weekday-number'])

	def test_mid_year_period_day(self):
		"""Test the period day in the middle of the year."""
		self.assertEqual(1, self.calendar.current_year[45]['weekday-period-day'])

	def test_mid_year_period_name(self):
		"""Test the period name in the middle of the year."""
		self.assertEqual('Tuesday', self.calendar.current_year[45]['weekday-period'])

if __name__ == '__main__':
	unittest.main()
