"""
gtime.py

A module for general, low-precision time tracking.

Classes:
Alarm: An event that triggers at a given time. (object)
AlarmByEvent: An alarm that is triggered by a specific event. (object)
AlarmByTime: An alarm that is triggered at a specific time. (object)
Time: A time, precise to the minute, with months. (object)
"""

import functools
import re

class Alarm(object):
	"""
	An event that triggers at a given time. (object)

	Attributes:
	done: A flag for the alarm being finished. (bool)
	note: The message displayed when the alarm goes off. (str)
	repeat: A flag for repeating the alarm after it goes off. (bool)
	trigger: The event that causes the alarm to go off. (Time or str)

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
		repeat: A flag for repeating the alarm after it goes off. (bool)
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

class AlarmByEvent(object):
	"""
	An alarm that is triggered by a specific event. (object)

	Methods:
	check: See if the alarm has been triggered. (None)
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

class AlarmByTime(object):
	"""
	An alarm that is triggered at a specific time. (object)

	Methods:
	check: See if the alarm has been triggered. (None)
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
	# Parse the arguments.
	symbol, time_spec, note = arguments.split(None, 2)
	# Check for time variable alarms.
	if time_spec.lower() in events:
		alarm = AlarmByEvent(time_spec.lower(), note, symbol == '@')
	else:
		# Convert the time.
		if '-' in time_spec and '/' not in time_spec:
			time_spec = f'0/{time_spec}'
		time = gtime.Time.from_str(time_spec.replace(' ', '-'))
		# Set the alarm time.
		if symbol = '+':
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