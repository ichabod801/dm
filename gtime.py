"""
gtime.py

A module for general, low-precision time tracking.

Classes:
Time: A time, precise to the minute, with months. (object)
"""

import functools

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

	Overridden Methods:
	__init__
	__add__
	__eq__
	__lt__
	__repr__
	__str__
	"""

	def __init__(year = 1, day = 1, hour = 0, minute = 0):
		"""
		Set the time. (None)

		Parameters:
		year: The year. (int)
		day: The day within the year. (int)
		hour: The hour within the day. (int)
		minute: The minute within the hour. (int)
		"""
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
		extra, minute = divmod(minute, 60)
		hour += extra
		extra, hour = divmod(hour, 24)
		day += extra
		extra, day = divmod(day, 365)
		year += extra
		# Return the time.
		return Time(year, day, hour, minute)

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
		return f'Day {self.day} of Year {self.year}, {self.hour}:{self.minute:02}'

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
		extra, minute = divmod(minute, 60)
		hour += extra
		extra, hour = divmod(hour, 24)
		day += extra
		extra, day = divmod(day, 365)
		year += extra
		# Return the time.
		return Time(year, day, hour, minute)
