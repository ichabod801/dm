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

if __name__ == '__main__':
	unittest.main()
