"""
gtime.py

A module for general, low-precision time tracking.

Classes:
Alarm: An event that triggers at a given time. (object)
AlarmByEvent: An alarm that is triggered by a specific event. (Alarm)
AlarmByTime: An alarm that is triggered at a specific time. (Alarm)
Calendar: A system for giving a unique identifier to each day. (object)
Cycle: A repeating sequence of defined periods in a calendar. (object)
Deviation: A change from the normal number of days in a period. (namedtuple)
Period: A named set of days within a calendar cycle. (namedtuple)
Time: A time, precise to the minute, with months. (object)
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

class DeviationCalendar(object):
	"""
	A calender using integers and planned deviations. (object)

	# !! redo to drop year_deviations, and calculate year_length from months.

	Attributes:
	calculated_years: The pre-calculated number of days per year. (list of int)
	month_deviations: Deviations in the length of months. (list of Deviation)
	months: The months of the year and their length in days. (dict of str: int)
	year_deviations: Deviations in the length of the year. (list of Deviation)
	year_length: The length of the standard year in days. (int)

	Methods:
	days_in_year: Calculate how many days there are in a given year. (int)
	days_to_year: Calculate how many days there are before a given year. (int)
	months_in_year: Calculate the month lengths for a given year. (dict)

	Overridden Methods:
	__init__
	"""

	def __init__(self, year_length, months, year_deviations, month_deviations):
		"""
		Set up the calendar structure. (None)

		Parameters:
		year_length: The length of the year in days. (int)
		months: The months of the year and their length in days. (dict of str: int)
		year_deviations: Deviations in the length of the year. (list of Deviation)
		month_deviations: Deviations in the length of months. (list of Deviation)
		"""
		self.year_length = year_length
		self.year_deviations = year_deviations
		self.months = months
		self.month_deviations = month_deviations
		self.calculated_years = [0]

	def days_in_year(self, year):
		"""
		Calculate how many days there are in a given year. (int)

		Parameters:
		year: The year to calculate the number of days for. (int)
		"""
		# Calculate deviations from base.
		days = self.year_length
		for deviation in year_deviations:
			if deviation.function(year):
				days = deviation.new_value
		return days

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
		# Calculate the deviations from base months.
		year_months = self.months.copy()
		for deviation in month_deviations:
			if deviation.function(year):
				year_months[deviation.period] = deviation.new_value
		return year_months

class FractionalCalendar(object):
	"""
	A calendar using fractional year lengths. (object)

	Attributes:
	months: The months of the year and their length in days. (dict of str: int)
	overage_month: The month getting an extra day in a long year. (str)
	year_length: The number of days in the year. (float)

	Methods:

	Overridden Methods:
	__init__
	"""

	def __init__(self, year_length, months, overage_month):
		"""
		Set up the calendar structure. (None)

		Parameters:
		year_length: The number of days in the year. (float)
		months: The months of the year and their length in days. (dict of str: int)
		overage_month: overage_month: The month getting an extra day in a long year. (str)
		"""
		self.year_length = year_length
		self.months = months
		self.overage_month = overage_month

	def days_in_year(self, year):
		"""
		Calculate how many days there are in a given year. (int)

		Parameters:
		year: The year to calculate the number of days for. (int)
		"""
		# Calculate last year's overage to see if this year crosses the 0.5 line.
		previous_days = (year - 1) * self.year_length
		previous_fraction = previous_days - int(previous_days)
		return round(year * self.year_length + previous_fraction, 0)

	def days_to_year(self, year):
		"""
		Calculate how many days there are before a given year. (int)

		Parameters:
		year: The year to calculate the number of days before. (int)
		"""
		# This is simple multiplication for this type of calendar.
		return round((year - 1) * year_length, 0)

	def months_in_year(self, year):
		"""
		Calculate the month lengths for a given year. (dict of str: int)

		Parameters:
		year: The year to calculate the length of the months for. (int)
		"""
		# Add to the overage month if it's a longer year.
		year_months = self.months.copy()
		if days_in_year(year) > self.year_length:
			year_months[self.overage_month] += 1
		return year_months

class Cycle(object):
	"""
	A repeating sequence of defined periods in a calendar. (object)

	Cycles include things like weeks, months, and zodiacs.

	Attributes:
	description: A description of the cycle. (str)
	deviation: The exceptions to the standard period definitions. (str)
	format_text: The default text formatting for the cycle. (str)
	name: The name of the cycle. (str)
	periods: The periods that make up the cycle. (tuple)
	singular: The singular form of the name, for formatting. (str)
	zero: The day the cycle starts. (Time)

	Methods:
	backward: Move backward the given number of days in the cycle. (None)
	forward: Move forward the given number of days in the cycle. (None)
	year_periods: Determine the periods for a given year. (None)

	Overridden Methods:
	__init__
	"""

	def __init__(self, node):
		"""
		Parse the cycle's definition. (None)

		Parameters:
		node: The document section contianing the definition. (HeaderNode)
		"""
		# Set the default values of the attributes.
		self.name = node.name
		self.description = ''
		self.periods = {}
		self.deviations = []
		self.start = 1
		# Parse out the lines of the definition.
		table = []
		for line in node.children[0]:
			# Assume pipe-table lines define the periods.
			if line.startswith('|'):
				table.append(line)
			# Parse out deviations.
			elif line.lower().startswith('**deviation**'):
				period, new_value, method, divisor, *remainders = line[13:].split(',')
				divisor = int(divisor)
				remainers = [int(word) for word in remainders]
				function = lambda data: data[method.strip()] % divisor in remainders
				self.deviations.append(Deviation(period.strip(), int(new_value), function))
			elif line.lower().startswith('**start**'):
				self.start = int(line[9:])
		# Parse out the periods.
		for line in table[2:]:
			name, abbreviation, number, days = line.split('|')[1:]
			self.periods[name.strip()] = {'abbreviation': abbreviation.strip(), 'number': int(number)}
			self.periods[name.strip()]['days'] = float(days)
		# Get the default text formatting.
		header = table[0].split('|')
		self.singular = header[1]
		if max(period.number for period in self.periods) == 1:
			self.format_text = f'{{{self.singular}}}'
		else:
			self.format_text = f'{{{self.singular}}} {{{self.singular}-day}}'
		# Get the initial state of the cycle.
		self.state = {'cycle-day': self.start, 'cycle': 1, 'year': 1, 'periods': self.get_periods(1, 1)}
		start = self.start
		for period in self.state['periods']:
			if start <= period.days:
				self.state['current-period'] = period
				self.state['period-day'] = start
				break
			else:
				start -= period.days

	def advance(self, days, year):
		"""
		Advance the cycle. (None)

		Parameters:
		days: The number of days to advance the cycle. (int)
		year: The number of the year after advancement. (int)
		"""
		# !! the year being separate is a big problem.

	def get_periods(self, cycle, year):
		"""
		Get the periods for a certain year and cycle. (list of tuple)

		Parameters:
		cycle: The number of the current cycle. (int)
		year: The number of the current year. (int)
		"""
		data = {'cycle': cycle, 'year': year}
		periods = {name: spec.copy() for name, spec in self.periods}
		for deviation in self.deviations:
			if deviation.function(data):
				periods[deviation.period] = period.new_value
		return periods

# A change from the normal number of days in a period. (namedtuple)
Deviation = collections.namedtuple('Deviation', ('period', 'new_value', 'function'))

# A named set of days within a calendar cycle. (namedtuple)
Period = collections.namedtuple('Period', ('name', 'abbreviation', 'number', 'days'))

@functools.total_ordering
class Time(object):
	"""
	A time, precise to the minute, with months. (object)

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
		extra, day = divmod(day, 365)
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
