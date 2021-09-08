"""
gtime.py

A module for general, low-precision time tracking.

Classes:
Alarm: An event that triggers at a given time. (object)
AlarmByEvent: An alarm that is triggered by a specific event. (Alarm)
AlarmByTime: An alarm that is triggered at a specific time. (Alarm)
Calendar: A static calendar. (object)
DeviationCalendar: A calender using integers and planned deviations. (Calendar)
FractionalCalendar: A calendar using fractional year lengths. (Calendar)
FractionalCycle: A cycle of days based on a fractional number of days. (object)
StaticCycle: A calendar cycle that never changes. (object)
Deviation: A change from the normal number of days in a period. (namedtuple)
Time: A time, precise to the minute, with months. (object)

Functions:
new_alarm: Create a new alarm. (Alarm)
parse_calendar: Parse a text definition of a calendar. (Calendar)
parse_cycle: Parse a text definition of a calendar cycle. (Cycle)
"""

import collections
import functools
import re

class Alarm(object):
	"""
	An event that triggers at a given time. (object)

	Attributes:
	done: A flag for the alarm being finished. (bool)
	note: The message displayed when the alarm goes off. (str)
	repeat: A flag for repeating the alarm after it goes off. (bool or Time)
	trigger: The event that causes the alarm to go off. (Time or str)

	Class Methods:
	from_data: Create an alarm from the storage text. (Alarm)

	Overridden Methods:
	__init__
	__str__
	__repr__
	"""

	def __init__(self, trigger, note, repeat):
		"""
		Set up the alarm. (None)

		Parameters:
		trigger: The event that causes the alarm to go off. (Time or str)
		note: The message displayed when the alarm goes off. (str)
		repeat: A flag for repeating the alarm after it goes off. (bool or Time)
		"""
		# Set the given attributes.
		self.trigger = trigger
		self.note = note
		self.repeat = repeat
		# Set the default attributes.
		self.done = False

	def __repr__(self):
		"""Debugging text representation."""
		text = f'<Alarm {self.trigger} {self.note[:20]!r}'
		if self.repeat:
			text = f'{text} @>'
		else:
			text = f'{text}>'
		return text

	def __str__(self):
		"""Human readable text representation."""
		if self.repeat:
			text = 'Repeating alarm at'
		else:
			text = 'Alarm at'
		return f'{text} {self.trigger}; {self.note}'

	@classmethod
	def from_data(self, data):
		"""Create an alarm from the storage text. (Alarm)"""
		if data.startswith('event'):
			return AlarmByEvent.from_data(data)
		elif data.startswith('time'):
			return AlarmByTime.from_data(data)
		else:
			raise ValueError(f'Invalid alarm data: {data!r}.')

class AlarmByEvent(Alarm):
	"""
	An alarm that is triggered by a specific event. (Alarm)

	Methods:
	check: See if the alarm has been triggered. (None)
	data: Storage text representation. (str)

	Class Methods:
	from_data: Create an alarm from the storage text. (AlarmByEvent)
	"""

	def check(self, event, time):
		"""
		See if the alarm has been triggered. (None)

		Parameters:
		event: The event that has just happened. (str)
		time: The current time. (Time)
		"""
		if self.trigger.lower() == event.lower():
			print(f'ALARM: {self.note}')
			self.done = not self.repeat

	def data(self):
		"""Storage text representation. (str)"""
		return f'event {self.trigger} {self.repeat} {self.note}'

	@classmethod
	def from_data(self, data):
		"""Create an alarm from the storage text. (AlarmByEvent)"""
		event, trigger, repeat, note = data.split(None, 3)
		return AlarmByEvent(trigger, note, repeat == 'True')

class AlarmByTime(Alarm):
	"""
	An alarm that is triggered at a specific time. (Alarm)

	Methods:
	check: See if the alarm has been triggered. (None)
	data: Storage text representation. (str)

	Class Methods:
	from_data: Create an alarm from the storage text. (AlarmByTime)
	"""

	def check(self, event, time):
		"""
		See if the alarm has been triggered. (None)

		Parameters:
		event: The event that has just happened. (str)
		time: The current time. (Time)
		"""
		while self.trigger <= time:
			print(f'ALARM: {self.note}')
			if self.repeat:
				self.trigger += self.repeat
			else:
				self.done = True
				break

	def data(self):
		"""Storage text representation. (str)"""
		trigger = self.trigger.short().replace(' ', '-')
		if self.repeat:
			repeat = self.repeat.short().replace(' ', '-')
		else:
			repeat = 'False'
		return f'time {trigger} {repeat} {self.note}'

	@classmethod
	def from_data(self, data):
		"""Create an alarm from the storage text. (AlarmByEvent)"""
		time, trigger, repeat, note = data.split(None, 3)
		trigger = Time.from_str(trigger.replace('-', ' '))
		if repeat == 'False':
			repeat = False
		else:
			repeat = Time.from_str(repeat.replace('-', ' '))
		return AlarmByTime(trigger, note, repeat)

class Calendar(object):
	"""
	A static calendar. (object)

	The months attribute is the names of the months as keys, with the days in each
	month as the values.

	Attributes:
	current_year: The current year's table from year_table. (dict)
	cycles: The other cycles in the year. (list of Cycle)
	formats: The formats for showing dates. (dict of str: str)
	months: The months of the year and their length in days. (dict of str: int)

	Methods:
	days_in_year: Calculate how many days there are in a given year. (int)
	days_to_year: Calculate how many days there are before a given year. (int)
	date: Return a formatted date string. (str)
	set_year: The the current year for the calendar. (None)
	year_table: Calculate a table of days for the year. (dict)

	Overridden Methods:
	__init__
	"""

	def __init__(self, months, cycles = [], formats = {}):
		"""
		Set up the calendar structure. (None)

		Parameters:
		months: The months of the year and their length in days. (dict of str: int)
		cycles: The other cycles in the year. (list of Cycle)
		formats: The formats for showing dates. (dict of str: str)
		"""
		# Set the given attributes.
		self.months = months
		self.cycles = cycles
		self.formats = {'default': '{month-name} {day-of-month}'}
		self.formats.update(formats)
		# Calculate the first year.
		self.set_year(1)

	def days_in_year(self, year):
		"""
		Calculate how many days are in a given year. (int)

		Parameters:
		year: The year to get the number of days for. (int)
		"""
		return sum(self.months.values())

	def days_to_year(self, year):
		"""
		Calculate how many days there are before a given year. (int)

		Parameters:
		year: The year to calculate the number of days before. (int)
		"""
		return sum(self.months.values()) * (year - 1)

	def date(self, day, format_name = 'default'):
		"""
		Return a formatted date string. (str)

		Parameters:
		day: The day of the current year. (int)
		format_name: The name of the format to use. (str)
		"""
		return self.formats[format_name].format(**self.current_year[day])

	def set_year(self, year):
		"""
		Set the current year of the calendar. (None)

		Parameters:
		year: The year to set the calendar to. (int)
		"""
		self.current_year = self.year_table(year)

	def year_table(self, year):
		"""
		Calculate a table of days for the year. (dict)

		Parameters:
		year: The year to set the calendar to. (int)
		"""
		year_day = 0
		month_number = 0
		table = {'year': year, 'year-length': sum(self.months.values())}
		for name, days in self.months.items():
			month_number += 1
			for day in range(days):
				year_day += 1
				table[year_day] = {'day-of-year': year_day, 'day-of-month': day + 1, 'month-name': name,
					'month-number': month_number}
		for cycle in self.cycles:
			cycle.expand_table(table, self)
		return table

class DeviationCalendar(Calendar):
	"""
	A calender using integers and planned deviations. (Calendar)

	Calendars work by creating a year table, which has every day of the year in
	it, with information about that day. See the year_table method documentation
	for details. 

	Attributes:
	calculated_years: The pre-calculated number of days per year. (list of int)
	month_deviations: Deviations in the length of months. (list of Deviation)
	year_length: The length of the standard year in days. (int)

	Methods:
	months_in_year: Calculate the month lengths for a given year. (dict)

	Overridden Methods:
	__init__
	days_in_year
	days_to_year
	year_table
	"""

	def __init__(self, months, month_deviations = [], cycles = [], formats = {}):
		"""
		Set up the calendar structure. (None)

		Parameters:
		months: The months of the year and their length in days. (dict of str: int)
		month_deviations: Deviations in the length of months. (list of Deviation)
		cycles: The other cycles in the year. (list of Cycle)
		formats: The formats for showing dates. (dict of str: str)
		"""
		# Do deviation specific set up.
		self.calculated_years = [0]
		self.month_deviations = month_deviations
		self.year_length = sum(months.values())
		# Do the base setup.
		super().__init__(months, cycles, formats)

	def days_in_year(self, year):
		"""
		Calculate how many days are in a given year. (int)

		Parameters:
		year: The year to get the number of days for. (int)
		"""
		# Calculate from months if not already calculated.
		if year <= len(self.calculated_years):
			return sum(self.months_in_year(year).values())
		else:
			return self.calculated_years[year]

	def days_to_year(self, year):
		"""
		Calculate how many days there are before a given year. (int)

		Parameters:
		year: The year to calculate the number of days before. (int)
		"""
		# Calculate for each year not calculated yet.
		total = sum(self.calculated_years[:year])
		for sub_year in range(len(self.calculated_years), year):
			days = self.days_in_year(sub_year)
			self.calculated_years.append(days)
			total += days
		return total

	def months_in_year(self, year):
		"""
		Calculate the month lengths for a given year. (dict of str: int)

		Parameters:
		year: The year to calculate the length of the months for. (int)
		"""
		data = {'year': year}
		# Calculate the deviations from base months.
		year_months = self.months.copy()
		for deviation in self.month_deviations:
			if deviation.function(data):
				year_months[deviation.period] = deviation.new_value
		return year_months

	def year_table(self, year):
		"""
		Calculate a table of days for the year. (dict)

		The year table is a dict with a key for each day by number in the year. The
		value for that day is a dict of the following keys:
			* day-of-year: The day's sequence within the year.
			* day-of-month: The day's sequence within the day's month.
			* month-name: The name of the month the day is in.
			* month-number: The number of the month within the year.
		There are two string keys to the year table as well:
			* year: The year the table is for.
			* year-length: The number of days in the year.

		Parameter:
		year: The year to calculate a table for. (int)
		"""
		# Get the data for the year.
		year_months = self.months_in_year(year)
		year_length = sum(year_months.values())
		# Loop through days building a year table.
		year_day = 0
		month_number = 0
		table = {'year': year, 'year-length': year_length}
		for name, days in year_months.items():
			month_number += 1
			for day in range(days):
				year_day += 1
				table[year_day] = {'day-of-year': year_day, 'day-of-month': day + 1, 'month-name': name,
					'month-number': month_number}
		# Expand the table with any cycles.
		for cycle in self.cycles:
			cycle.expand_table(table, self)
		return table

class FractionalCalendar(Calendar):
	"""
	A calendar using fractional year lengths. (Calendar)

	Calendars work by creating a year table, which has every day of the year in
	it, with information about that day. See the year_table method documentation
	for details. 

	Attributes:
	overage_month: The month getting an extra day in a long year. (str)
	year_length: The number of days in the year. (float)

	Methods:
	months_in_year: Calculate the month lengths for a given year. (dict)

	Overridden Methods:
	__init__
	days_in_year
	days_to_year
	year_table
	"""

	def __init__(self, year_length, months, overage_month, cycles = [], formats = {}):
		"""
		Set up the calendar structure. (None)

		Parameters:
		year_length: The number of days in the year. (float)
		months: The months of the year and their length in days. (dict of str: int)
		overage_month: overage_month: The month getting an extra day in a long year. (str)
		cycles: The non-month cycles of the calendar. (list of Cycle)
		formats: The date formats for the calendar. (dict of str: str)
		"""
		# Set the fractional specific attributes.
		self.year_length = year_length
		self.overage_month = overage_month
		# Set the base attributes.
		super().__init__(months, cycles, formats)

	def days_in_year(self, year):
		"""
		Calculate how many days there are in a given year. (int)

		Parameters:
		year: The year to calculate the number of days for. (int)
		"""
		# Calculate last year's overage to see if this year crosses the 0.5 line.
		previous_days = round((year - 1) * self.year_length, 0)
		return int(round(year * self.year_length - previous_days, 0))

	def days_to_year(self, year):
		"""
		Calculate how many days there are before a given year. (int)

		Parameters:
		year: The year to calculate the number of days before. (int)
		"""
		# This is simple multiplication for this type of calendar.
		return int(round((year - 1) * year_length, 0))

	def months_in_year(self, year):
		"""
		Calculate the month lengths for a given year. (dict of str: int)

		Parameters:
		year: The year to calculate the length of the months for. (int)
		"""
		# Add to the overage month if it's a longer year.
		year_months = self.months.copy()
		if self.days_in_year(year) > self.year_length:
			year_months[self.overage_month] += 1
		return year_months

	def year_table(self, year):
		"""
		Calculate a table of days for the year. (dict)

		The year table is a dict with a key for each day by number in the year. The
		value for that day is a dict of the following keys:
			* day-of-year: The day's sequence within the year.
			* day-of-month: The day's sequence within the day's month.
			* month-name: The name of the month the day is in.
			* month-number: The number of the month within the year.
		There are two string keys to the year table as well:
			* year: The year the table is for.
			* year-length: The number of days in the year.

		Parameter:
		year: The year to calculate a table for. (int)
		"""
		# Get the data for the year.
		year_length = self.days_in_year(year)
		year_months = self.months_in_year(year)
		months = list(year_months.items())
		months.reverse()
		# Loop through days building a year table.
		table = {'year': year, 'year-length': year_length}
		month_day = 1
		month_number = 1
		month, month_length = months.pop()
		for day in range(1, year_length + 1):
			table[day] = {'day-of-year': day, 'day-of-month': month_day, 'month-name': month,
				'month-number': month_number}
			month_day += 1
			# Check for the next month
			if month_day > month_length:
				month_day = 1
				month_number += 1
				if day != year_length:
					month, month_length = months.pop()
		for cycle in self.cycles:
			cycle.expand_table(table, self)
		return table

class FractionalCycle(object):
	"""
	A calendar cycle based on a fractional number of days. (object)

	Attributes:
	keys: The unique keys for the cycle in year tables. (dict of str: str)
	name: The name of the cycle. (str)
	period_length: The length in days of a period in the cycle. (float)
	periods: The name of the groups of days in the cycle. (list of str)

	Methods:
	advance_state: Advance a cycle state by one day. (None)
	expand_table: Expand a year table to include this cycle. (None)

	Overridden Methods:
	__init__
	"""

	def __init__(self, name, periods, period_length):
		"""
		Set up the cycle's attributes. (None)

		Parameters:
		name: The name of the cycle. (str)
		periods: The name of the groups of days in the cycle. (list of str)
		period_length: The length in days of a period in the cycle. (float)
		"""
		# Set the given attributes.
		self.name = name
		self.periods = periods
		self.period_length = period_length
		self.cycle_length = self.period_length * len(self.periods)
		# Calcuate keys unique to the cycle for year tables.
		low_name = name.lower()
		self.keys = {'number': f'{low_name}-number', 'day': f'{low_name}-day'}
		self.keys['period'] = f'{low_name}-period'
		self.keys['period-day'] = f'{low_name}-period-day'

	def advance_state(self, state, year = 0):
		"""
		Advance a cycle state by one day. (None)

		This method assumes year does not change if cycle repeats.

		Parameters:
		state: The cycle state to advance. (dict)
		year: The year the cycle is in. (int)
		"""
		# Advance the day state.
		state[self.keys['day']] += 1
		# Check for end of period.
		if state[self.keys['day']] > round(state['fractional-days']):
			# Check for end of cycle.
			if not state['period-list']:
				state[self.keys['number']] += 1
				state['period-list'] = [(period, state[self.keys['number']]) for period in self.periods]
				state[self.keys['period']], period_count = state['period-list'].pop(0)
				unused_fraction = state['fractional-days'] - int(state['fractional-days'])
				state['fractional-days'] = self.period_length + unused_fraction
				state[self.keys['day']] = 1
			else:
				old_cycle = state[self.keys['number']]
				state[self.keys['period']], state[self.keys['number']] = state['period-list'].pop(0)
				# Check for end of cycle due to overage period.
				if old_cycle == state[self.keys['number']]:
					state['fractional-days'] += self.period_length
				else:
					state[self.keys['day']] = 1
					unused_fraction = state['fractional-days'] - int(state['fractional-days'])
					state['fractional-days'] = self.period_length + unused_fraction
			state[self.keys['period-day']] = 1
		else:
			state[self.keys['period-day']] += 1

	def expand_table(self, year_table, calendar):
		"""
		Expand a year table to include this cycle. (None)

		Wait: The phase of the moon (start period day) can be calcuated by total days.
			maybe that should be the first calculation.
			this one google might actually be useful one. (No, they use geometry not generally applicable)

		Parameters:
		year_table: The days of the year and their attributes. (dict)
		calendar: The calendar that made the year table. (Calendar)
		"""
		# Get the overage from last year.
		previous_days = calendar.days_to_year(year_table['year'])
		if self.cycle_length >= year_table['year-length']:
			cycle_count = year_table['year']
		else:
			cycle_count = int(previous_days / self.cycle_length) + 1
		total_length = (int(previous_days / self.period_length) + 1) * self.period_length
		overage = total_length - previous_days
		# Figure out which period when over.
		if year_table['year'] > 1 and overage >= 0.5:
			# Get the period overlapping into this year.
			last_year = calendar.days_in_year(year_table['year'] - 1)
			last_year_periods = int((last_year + overage) / self.period_length)
			overage_period = self.periods[last_year_periods - 1]
			period_list = [(overage_period, cycle_count - 1)]
			# Calculate which day in that period is the first of the year.
			overage_days = int(round(overage, 0))
			# Get last year's overage
			last_period_count = int((previous_days - last_year) / self.period_length) + 1
			last_total_length = last_period_count * self.period_length
			last_overage = last_total_length - last_year
			# Get days in the overlapping period
			upto_last_period = int(round(last_total_length - self.period_length, 0))
			last_period_days = int(round(last_total_length - upto_last_period, 0))
			start_period_day = ((previous_days / self.period_length) % 1) * self.period_length
			start_period_day = int(round(start_period_day, 0)) + 1
			start_day = int(round(self.cycle_length)) - (last_period_days - start_period_day)
			# Get the fractional days.
			fractional_days = self.cycle_length + overage - int(overage)
			fractional_days = self.cycle_length
			fractional_days = overage + start_day - 1
		else:
			period_list = []
			start_day = 1
			start_period_day = 1
			fractional_days = self.period_length + overage - int(overage)
			fractional_days = self.period_length
		# Expand the full period list.
		period_list += [(period, cycle_count) for period in self.periods]
		# Get the initial state.
		state = {self.keys['number']: period_list[0][1], self.keys['day']: start_day}
		state[self.keys['period']] = period_list[0][0]
		state[self.keys['period-day']] = start_period_day
		state['fractional-days'] = fractional_days
		state['period-list'] = period_list[1:]
		# Cycle on from there.
		for day in range(1, year_table['year-length'] + 1):
			year_table[day].update(state)
			#del year_table[day]['fractional-days']
			del year_table[day]['period-list']
			self.advance_state(state)

class StaticCycle(object):
	"""
	A calendar cycle that never changes. (object)

	Attributes:
	cycle: The total number of days in the cycle. (int)
	keys: The keys for the cycle data on the year table. (dict of str: str)
	name: The name of the cycle. (str)
	periods: The periods of the cycle. (dict of str: int)

	Methods:
	advance_state: Advance a cycle state by one day. (None)
	expand_table: Expand a year table to include this cycle. (None)

	Overridden Methods:
	__init__
	"""

	def __init__(self, name, periods):
		"""
		Set up the cycle definition. (None)

		Parameters:
		name: The name of the cycle. (str)
		periods: The periods of the cycle. (dict of str: int)
		"""
		# Set the given paramters.
		self.name = name
		self.periods = periods
		# Calculate the cycle length.
		self.cycle_length = sum(periods.values())
		# Set up unique cycle keys for the year table.
		low_name = self.name.lower()
		self.keys = {'number': f'{low_name}-number', 'day': f'{low_name}-day'}
		self.keys['period'] = f'{low_name}-period'
		self.keys['period-day'] = f'{low_name}-period-day'

	def advance_state(self, state, year = 0):
		"""
		Advance a cycle state by one day. (None)

		This method assumes year does not change if cycle repeats.

		Parameters:
		state: The cycle state to advance. (dict)
		year: The year the cycle is in. (int)
		"""
		# Get the periods.
		period_order = list(self.periods.keys())
		# Advance the day state.
		state[self.keys['day']] += 1
		# Check for end of cycle.
		if state[self.keys['day']] > sum(self.periods.values()):
			state[self.keys['number']] += 1
			state[self.keys['day']] = 1
			state[self.keys['period-day']] = 1
			state[self.keys['period']] = period_order[0]
		# Check for end of period.
		elif state[self.keys['period-day']] + 1 > self.periods[state[self.keys['period']]]:
			state[self.keys['period-day']] = 1
			state[self.keys['period']] = period_order[period_order.index(state[self.keys['period']]) + 1]
		# Otherwise just advance state day.
		else:
			state[self.keys['period-day']] += 1

	def expand_table(self, year_table, calendar):
		"""
		Expand a year table to include this cycle. (None)

		Parameters:
		year_table: The days of the year and their attributes. (dict)
		calendar: The calendar that made the year table. (Calendar)
		"""
		# Calculate the starting cycle and day.
		previous_days = calendar.days_to_year(year_table['year'])
		cycles, overage = divmod(previous_days, self.cycle_length)
		cycles += 1
		state = {self.keys['number']: cycles, self.keys['day']: overage + 1}
		# Figure out where in the cycle you are.
		period_days = list(self.periods.items())
		period_days.reverse()
		if overage:
			while True:
				period, days_in_period = period_days.pop()
				if overage >= days_in_period:
					overage -= days_in_period
				else:
					state[self.keys['period']] = period
					state[self.keys['period-day']] = overage + 1
					break
		else:
			state[self.keys['period']] = period_days[-1][0]
			state[self.keys['period-day']] = 1
		# Cycle on from there.
		for day in range(1, year_table['year-length'] + 1):
			year_table[day].update(state)
			self.advance_state(state)

# A change from the normal number of days in a period. (namedtuple)
Deviation = collections.namedtuple('Deviation', ('period', 'new_value', 'function'))

@functools.total_ordering
class Time(object):
	"""
	A time, precise to the minute, with years. (object)

	Time objects add and subtract with other time objects, tuples, and ints.
	Tuples are converted to time objects assuming they are of the form (year,
	day, hour, minute). If they are shorter than four times, zeros are appended
	at the beginning. For example, (1, 30) is assumed to be one hour and thirty
	minutes. Ints are always assumed to be a number of minutes.

	Time objects sort and compare as if they were tuples of (year, day, hour,
	minute).

	Attributes:
	day: The day within the year. (int)
	hour: The hour within the day. (int)
	minute: The minute within the hour. (int)
	year: The year. (int)

	Class Attributes:
	full_regex: A regular expression matching a full date/time. (Pattern)
	year_length: How many days are in a year. (int)

	Methods:
	_rollover_check: Check for rollover/under in time parts after math. (tuple)
	short: Short text representation. (str)

	Class Methods:
	from_str: Create a time from a string. (Time)

	Overridden Methods:
	__init__
	__add__
	__eq__
	__lt__
	__repr__
	__str__
	"""

	full_regex = re.compile(r'(\d+)/(\d+) (\d+):(\d\d?)')

	year_length = 365

	def __init__(self, year = 0, day = 0, hour = 0, minute = 0):
		"""
		Set the time. (None)

		Parameters:
		year: The year. (int)
		day: The day within the year. (int)
		hour: The hour within the day. (int)
		minute: The minute within the hour. (int)
		"""
		year, day, hour, minute = self._rollover_check(year, day, hour, minute)
		self.year = year
		self.day = day
		self.hour = hour
		self.minute = minute

	def __add__(self, other):
		"""Addition with other Times, tuples, or ints. (Time)"""
		# Get the attributes based on the other object.
		if isinstance(other, Time):
			# From Time objects.
			year = self.year + other.year
			day = self.day + other.day
			hour = self.hour + other.hour
			minute = self.minute + other.minute
		elif isinstance(other, tuple):
			# From tuples (expanded if necessary)
			while len(other) < 4:
				other = (0,) + other
			year = self.year + other[0]
			day = self.day + other[1]
			hour = self.hour + other[2]
			minute = self.minute + other[3]
		elif isinstance(other, int):
			# From self for integers.
			year, day, hour = self.year, self.day, self.hour
			minute = self.minute + other
		else:
			# Error value.
			return NotImplemented
		# Check for rollover in the attributes.
		return Time(*self._rollover_check(year, day, hour, minute))

	def __eq__(self, other):
		"""Equality check. (bool)"""
		return (self.year, self.day, self.hour, self.minute) == other

	def __lt__(self, other):
		"""Less than check. (bool)"""
		return (self.year, self.day, self.hour, self.minute) < other

	def __radd__(self, other):
		"""Right-handed addition. (Time)"""
		return self.__add__(other)

	def __rsub__(self, other):
		"""Right-handed subtraction. (Time)"""
		# Conver other to a Time instance and subtract.
		if isinstance(other, tuple):
			# From tuples (expanded if necessary)
			while len(other) < 4:
				other = (0,) + other
		elif isinstance(other, int):
			other = (0, 0, 0, other)
		return Time(*other).__sub__(self)

	def __repr__(self):
		"""Debugging text representation. (str)"""
		return f'Time({self.year}, {self.day}, {self.hour}, {self.minute})'

	def __str__(self):
		"""Human readable text representation. (str)"""
		return f'Year {self.year}, Day {self.day}, {self.hour}:{self.minute:02}'

	def __sub__(self, other):
		"""Addition with other Times, tuples, or ints. (Time)"""
		# Get the attributes based on the other object.
		if isinstance(other, Time):
			# From Time objects.
			year = self.year - other.year
			day = self.day - other.day
			hour = self.hour - other.hour
			minute = self.minute - other.minute
		elif isinstance(other, tuple):
			# From tuples (expanded if necessary)
			while len(other) < 4:
				other = (0,) + other
			year = self.year - other[0]
			day = self.day - other[1]
			hour = self.hour - other[2]
			minute = self.minute - other[3]
		elif isinstance(other, int):
			# From self for integers.
			year, day, hour = self.year, self.day, self.hour
			minute = self.minute - other
		else:
			# Error value.
			return NotImplemented
		# Check for rollunder in the attributes.
		return Time(*self._rollover_check(year, day, hour, minute))

	def _rollover_check(self, year, day, hour, minute):
		"""
		Check for rollover/under in time parts after math. (tuple)

		Parameters:
		year: The year. (int)
		day: The day within the year. (int)
		hour: The hour within the day. (int)
		minute: The minute within the hour. (int)
		"""
		extra, minute = divmod(minute, 60)
		hour += extra
		extra, hour = divmod(hour, 24)
		day += extra
		while day > self.year_length:
			year += 1
			day -= self.year_length
		year += extra
		return (year, day, hour, minute)

	@classmethod
	def from_str(cls, text):
		"""
		Create a time from a string. (Time)

		Parameters:
		text: The text to create a time from. (str)
		"""
		if text.isdigit():
			return Time(minute = int(text))
		elif cls.full_regex.match(text):
			params = [int(group) for group in cls.full_regex.match(text).groups()]
			return Time(*params)
		elif ':' in text:
			hour, minute = [int(number) for number in text.split(':')]
			return Time(hour = hour, minute = minute)
		elif '/' in text:
			year, day = [int(number) for number in text.split('/')]
			return Time(year, day)
		else:
			raise ValueError('Invalid time specification.')

	def short(self):
		"""Short text representation. (str)"""
		return f'{self.year}/{self.day} {self.hour}:{self.minute:02}'

def new_alarm(alarm_spec, now, events = {}):
	"""
	Create a new alarm. (Alarm)

	Parameters:
	alarm_spec: The user specification of the alarm. (str)
	now: The current game time. (Time)
	events: The valid events. (dict of str: str)
	"""
	# Parse the alarm specification.
	symbol, time_spec, note = alarm_spec.split(None, 2)
	# Check for time variable alarms.
	if time_spec.lower() in events:
		alarm = AlarmByEvent(time_spec.lower(), note, symbol == '@')
	else:
		# Convert the time.
		if '-' in time_spec and '/' not in time_spec:
			time_spec = f'0/{time_spec}'
		time = Time.from_str(time_spec.replace(' ', '-'))
		# Set the alarm time.
		if symbol == '+':
			trigger = now + time
			repeat = False
		elif symbol == '@':
			trigger = now + time
			repeat = time
		else:
			if '/' not in time_spec:
				time.year = now.year
			if '-' not in time_spec:
				time.day = now.day
			trigger = time
			repeat = False
		# Create the alarm.
		alarm = AlarmByTime(trigger, note, repeat)
	return alarm

def parse_calendar(root):
	"""
	Parse text defining a calendar. (DeviationCalendar or FractionalCalendar)

	Parameters:
	root: The root node of the document tree for the calendar. (HeaderNode)
	"""
	# Read the defining document.
	calendar_type = 'unknown'
	cycles, deviations = [], []
	formats = {}
	overage_month = ''
	for node in root.children:
		# Check the initial text for values.
		if hasattr(node, 'lines'):
			for line in node.lines:
				# Get days in a year.
				if line.lower().startswith('**days in year**'):
					day_text = line.split('**')[-1]
					# Differentiate fractional and deviation calendars.
					if '.' in day_text:
						days_in_year = float(day_text)
						calendar_type = 'fractional'
					else:
						days_in_year = int(day_text)
						calendar_type = 'deviation'
				# Get the overage month for fractional years.
				elif line.lower().startswith('**overage month**'):
					overage_month = line.split('**')[-1].strip()
					calendar_type = 'fractional'
		# Get the list of months.
		elif node.name.lower() == 'months':
			parse_months = False
			months = {}
			for line in node.children[0].lines:
				if parse_months:
					blank, name, days, *junk = line.split('|')
					months[name.strip()] = int(days)
				elif line.startswith('|----'):
					parse_months = True
		# Get the deviations.
		elif node.name.lower() == 'deviations':
			for line in node.children[0].lines:
				if ',' in line:
					month, new_days, mod, *values = line.split(',')
					int_mod = int(mod)
					int_values = [int(word) for word in values]
					# Done w/ defaults to capture loop values. Otherwise last value is used for all funcs.
					def func(data, mod = int_mod, values = int_values):
						return data['year'] % mod in values
					deviations.append(Deviation(month.strip(), int(new_days), func))
		# Get the cycles.
		elif node.name.lower() == 'cycles':
			for child in node.children:
				cycles.append(parse_cycle(child))
		# Get the formats.
		elif node.name.lower() == 'formats':
			for line in node.children[0].lines:
				if '**' in line:
					blank, name, format_str = line.split('**')
					formats[name] = format_str
	# Set up the calendar.
	if calendar_type == 'fractional':
		calendar = FractionalCalendar(days_in_year, months, overage_month, cycles, formats)
	else:
		calendar = DeviationCalendar(months, deviations, cycles, formats)
	return calendar

def parse_cycle(node):
	"""
	Parse a text definition of a calendar cycle. (FractionalCycle or StaticCycle)

	Parameters:
	node: The node of the document tree for the cycle. (HeaderNode)
	"""
	# Loop through the text of the description.
	cycle_type = 'static'
	period_mode = False
	periods = {}
	for line in node.children[0].lines:
		# Watch for period length definitions.
		if line.lower().startswith('**period length**'):
			period_length = float(line.split('**')[-1])
			cycle_type = 'fractional'
			periods = []
		# Assume tables define periods.
		elif line.startswith('|----'):
			period_mode = True
		# Parse tables lines based on inferred cycle type.
		elif period_mode and line.startswith('|'):
			if cycle_type == 'static':
				blank, name, days, *junk = line.split('|')
				periods[name.strip()] = int(days)
			else:
				blank, name, *junk = line.split('|')
				periods.append(name.strip())
	# Create cycle based on inferred cycle type.
	if cycle_type == 'static':
		cycle = StaticCycle(node.name, periods)
	else:
		cycle = FractionalCycle(node.name, periods, period_length)
	return cycle

if __name__ == '__main__':
	five_days = {'Wonday': 1, 'Doubleday': 1, 'Treeday': 1, 'Forday': 1, 'Fifday': 1}
	week = StaticCycle('week', five_days)
	moon = FractionalCycle('moon', ['Alpha', 'Beta', 'Gamma', 'Delta'], 25.31)
	thirds = Deviation('First', 30, lambda data: data['year'] % 3 == 0)
	dev_cal = DeviationCalendar({'First': 29, 'Second': 30, 'Third': 31}, [thirds], [week, moon])
	frac_cal = FractionalCalendar(90.334, {'First': 29, 'Second': 30, 'Third': 31}, 'First')
