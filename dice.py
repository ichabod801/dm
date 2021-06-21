"""
dice.py

Dice for dm.py.

The DICE_REGEX pattern has the following groups:
	0: The repeated die roll text
	1: The repeated die roll number
	2: The number of dice to roll, or the raw number if there are no other
		matching groups.
	3: The number of sides on the rolled die.
	4: The keep low text.
	5: The keep low number.
	6: The keep high text.
	7: The keep high number.

Constants:
DICE_REGEX: A regular expression for the die roll syntax. (Pattern)
TIGHT_REGEX: A regular expression for a die roll that requires sides. (Pattern)

Functions:
d20: Roll a d20, possibly with advantage. (int)
nd: Roll more than one die. (int)
roll: Do a complicated roll. (int or list of int)
"""

import random
import re

DICE_REGEX = re.compile(r'((\d*)x)?\s*(\d*)d(\d*)\s*(kl(\d*))?(kh(\d*))?')
TIGHT_REGEX = re.compile(r'((\d*)x)?\s*(\d*)d(\d+)\s*(kl(\d*))?(kh(\d*))?')

def d20(advantage = 0):
	"""
	Roll a d20. (int)

	The advantage parameter gives advantage if it is positive, gives
	disadvantage if it is negative, and does nothing if it is zero.

	Parameter:
	advantage: Whether the roll is done with advantage. (int)
	"""
	roll = random.randint(1, 20)
	if advantage:
		ad_roll = random.randint(1, 20)
		if advantage > 0:
			roll = max(roll, ad_roll)
		elif advantage < 0:
			roll = min(roll, ad_roll)
	return roll

def ndk(text):
	"""
	Roll more than one die. (int or list of int)

	Parameters:
	text: The text specifying the roll. (str)
	"""
	# Parse the roll text.
	parsed = DICE_REGEX.match(text).groups()
	repeat = int(parsed[1]) if parsed[1] else 1
	number = int(parsed[2]) if parsed[2] else 1
	try:
		sides = int(parsed[3])
	except ValueError:
		return 0
	keep_low = int(parsed[5]) if parsed[5] else 0
	keep_high = int(parsed[7]) if parsed[7] else 0
	# Roll the dice.
	values = []
	for roll in range(repeat):
		dice = [random.randint(1, sides) for die in range(number)]
		if keep_high:
			dice.sort()
			dice = dice[-keep_high:]
		if keep_low:
			dice.sort()
			dice = dice[:keep_low]
		values.append(sum(dice))
	# Return one or multiple values as directed.
	if repeat == 1:
		return values[0]
	else:
		return values

def roll(roll_text):
	"""
	Do a complicated roll. (int or list of int)

	Dice rolls are specified with '{n}d{s}', where n is the number of dice to
	roll and s is the number of sides each of those dice has. Note that n 
	defaults to 1 and s defaults to 20, so 'd6' rolls one six sider, and '2d'
	rolls two twenty siders.

	Dice rolls can be combined with other dice rolls or integers using any of
	the four basic mathematical operators: +, -, *, or / (integer division).

	Parameters:
	roll_text: The text specifying the roll. (str)
	"""
	# Parse out the values and the operators, rolling any dice that come up.
	op_symbols = set('+-*/')
	values, operators = [], []
	text = ''
	for char in roll_text:
		if char in op_symbols:
			text = text.strip()
			if text.isdigit():
				values.append(int(text))
			elif not text and char == '-':
				values.append(0)
			else:
				values.append(ndk(text))
			operators.append(char)
			text = ''
		else:
			text += char
	text = text.strip()
	if text.isdigit():
		values.append(int(text))
	else:
		values.append(ndk(text))
	# Handle multiplication and division.
	new_values, new_operators = values[:1], []
	for operator, value in zip(operators, values[1:]):
		if operator == '*':
			new_values[-1] *= value
		elif operator == '/':
			new_values[-1] //= value
		else:
			new_values.append(value)
			new_operators.append(operator)
	# Handle addition and subtraction.
	total = new_values[0]
	for operator, value in zip(new_operators, new_values[1:]):
		if operator == '+':
			total += value
		elif operator == '-':
			total -= value
	# Return the final value.
	return total

if __name__ == '__main__':
	tests = ['d20', '2d8', '3d6', '4d6kh3', '4d6 kh3', '5', '6x 4d6kh3', '6x4d6kh3', '2d20kl1',
		'1d8+2', '1d8 + 2', '2 + 3', '-2', 'fred']
	for test in tests:
		print(test, roll(test), DICE_REGEX.search(test).groups() if DICE_REGEX.search(test) else 'N/A')
	print()