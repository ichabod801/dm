"""
weather.py

A module for handling D&D weather.

Constants:
WEATHER_DATA: Weather stats by climate and season. (dict)

Functions:
precipitation: Generate a precipitation message. (str)
temperature: Generate a random temperature message. (tuple)
wind: Generate a random wind message. (str)
"""

from . import dice
from . import text

WEATHER_DATA = {'cold-arid':
	{'spring': (38, 64, -4), 'summer': (58, 92, -5), 'fall': (39, 69, -4), 'winter': (25, 46, -3)},
	'cold-desert':
	{'spring': (30, 54, -5), 'summer': (51, 77, -5), 'fall': (30, 58, -5), 'winter': (6, 28, -5)},
	'continental':
	{'spring': (34, 48, 0), 'summer': (58, 74, 0), 'fall': (44, 56, 0), 'winter': (17, 32, 0)},
	'hot-arid':
	{'spring': (52, 78, -4), 'summer': (64, 92, -4), 'fall': (58, 77, -4), 'winter': (41, 62, -3)},
	'hot-desert':
	{'spring': (63, 90, -5), 'summer': (77, 102, -5), 'fall': (66, 84, -5), 'winter': (43, 66, -5)},
	'ice-cap':
	{'spring': (-90, -78, -5), 'summer': (-36, -16, -5), 'fall': (-82, -60, -5), 'winter': (-95, -80, -5)},
	'mediterranean':
	{'spring': (48, 65, +1), 'summer': (61, 78, -4), 'fall': (54, 69, +1), 'winter': (41, 57, +1)},
	'monsoon':
	{'spring': (72, 92, -4), 'summer': (69, 86, +5), 'fall': (69, 88, +3), 'winter': (66, 90, -5)},
	'oceanic':
	{'spring': (44, 56, +1), 'summer': (57, 72, -2), 'fall': (47, 57, +1), 'winter': (37, 44, +1)},
	'rainforest':
	{'spring': (74, 92, +3), 'summer': (72, 91, -1), 'fall': (73, 91, +4), 'winter': (73, 90, +3)},
	'sub-arctic':
	{'spring': (29, 45, -5), 'summer': (52, 66, -3), 'fall': (29, 41,-2), 'winter': (11, 23, -5)},
	'sub-polar':
	{'spring': (37, 45, 0), 'summer': (48, 55, 0), 'fall': (42, 49, +1), 'winter': (35, 42, +1)},
	'sub-tropical':
	{'spring': (53, 73, 0), 'summer': (64, 83, -2), 'fall': (59, 78, 0), 'winter': (48, 58, +3)},
	'temperate':
	{'spring': (45, 59, 0), 'summer': (56, 69, -1), 'fall': (50, 63, +1), 'winter': (41, 50, +2)},
	'tundra':
	{'spring': (3, 16, -5), 'summer': (37, 45, -4), 'fall': (16, 25, -4), 'winter': (-4, 9, -4)}}

def precipitation(climate, season, temp_low, temp_high):
	"""
	Generate a precipitation message. (str)

	Parameters:
	climate: A climate in WEATHER_DATA. (str)
	season: The season of the year. (str)
	temp_low: The low temperature for the day. (int)
	temp_high: The high temperature for the day. (int)
	"""
	# Get the precipitation type.
	if temp_high < 32:
		precip_word = 'snow'
	elif temp_low < 32:
		precip_word = 'rain/snow'
	else:
		precip_word = 'rain'
	# Get the precipitation amount.
	avg_low, avg_high, precip_mod = WEATHER_DATA[climate][season]
	precip_roll = dice.d20() + precip_mod
	if precip_roll < 13:
		message = f'There is no {precip_word} today.'
	elif precip_roll < 18:
		message = f'There is light {precip_word} today.'
	else:
		message = f'There is heavy {precip_word} today.{text.HEAVY_PRECIPITATION}'
	return message.strip()

def temperature(climate, season, roll_text):
	"""
	Generate a random temperature message. (tuple)

	The return value is the low temperature, the high temperature, and a message
	giving the temperature.

	Parameters:
	climate: A climate in WEATHER_DATA. (str)
	season: The season of the year. (str)
	roll_text: The roll for how high/low the temperature is. (str)
	"""
	temp_low, temp_high, precip_mod = WEATHER_DATA[climate][season]
	# Get the day's temperature.
	temp_roll = dice.d20()
	offset_roll = dice.roll(roll_text)
	if 15 <= temp_roll <= 17:
		temp_low -= offset_roll
		temp_high -= offset_roll
	elif temp_roll > 17:
		temp_low += offset_roll
		temp_high += offset_roll
	# Generate the message.
	message = f'The temperature ranges from a low of {temp_low}F to a high of {temp_high}F.'
	if temp_low <= 0:
		message = f'{message}{text.EXTREME_COLD}'
	if temp_high >= 100:
		message = f'{message}{text.EXTREME_HEAT}'
	return temp_low, temp_high, message.strip()

def wind():
	"""Generate a random wind message. (str)"""
	wind_roll = dice.d20()
	if wind_roll < 13:
		message = 'There is little to no wind today.'
	elif wind_roll < 18:
		message = 'There is a light wind today.'
	else:
		message = f'There is a strong wind today.{text.STRONG_WIND}'
	return message.strip()
