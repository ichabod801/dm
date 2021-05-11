"""
egor.py

A command line interface for a D&D DM helper.

Constants:
HELP_GENERAL: The general help text for Egor. (str)

Classes:
Egor: A helper for a D&D Dungeon master. (cmd.Cmd)
"""

import cmd
import re
import textwrap
import traceback

import dice
import srd
import gtime

HELP_GENERAL = """
You can use the roll command to roll dice, in all sorts of combinations. The
basic syntax is NdS to roll N dice with S sides. See 'help roll' for more
details and possibilities.

Egor can track the in-game time for you. The time command can set and report
the current game time, and the day command can advance the time in day 
increments. You can also set alarms in game time to alert you of events that
should happen, using the alarm command.
"""

class Egor(cmd.Cmd):
	"""
	A helper for a D&D Dungeon master. (cmd.Cmd)

	Attributes:
	alarms: Alarms that have been set based on self.time. (list of tuple)
	srd: The stored Source Resource Document for D&D. (SRD)
	time: The current game time. (gtime.Time)

	Class Attributes:
	aliases: Different names for commands. (dict of str: str)
	help_text: Additional help text. (dict of str: str)

	Methods:
	alarm_check: Check for any alarms that should have gone off. (None)
	do_alarm: Set an alarm. (None)
	do_day: Advance the time by day increments. (None)
	do_quit: Exit the Egor interface. (True)
	do_roll: Roll some dice. (None)
	do_srd: Search the Source Resource Document. (None)
	do_time: Update the current game time. (None)

	Overridden Methods:
	default
	do_help
	do_shell
	onecmd
	postcmd
	precmd
	preloop
	"""

	aliases = {'q': 'quit', 'r': 'roll', 't': 'time'}
	intro = 'Welcome, Master of Dungeons.\nI am Egor, allow me to assist you.\n'
	help_text = {}
	prompt = 'Yes, master? '

	def alarm_check(self, time_spec):
		"""
		Check for any alarms that should have gone off. (None)

		Parameters:
		time_spec: The user input that changed the time. (str)
		"""
		for alarm, note in self.alarms:
			if alarm <= self.time:
				print()
				print(f'ALARM at {alarm}: {note}')
		self.alarms = [(alarm, note) for alarm, note in self.alarms if alarm > self.time]

	def default(self, line):
		"""
		Handle unrecognized input. (bool)

		Parameters:
		line: The command entered by the user. (str)
		"""
		words = line.split()
		if words[0] in self.aliases:
			words[0] = self.aliases[words[0]]
			return self.onecmd(' '.join(words))
		elif dice.DICE_REGEX.search(line):
			self.do_roll(line)
		else:
			return super().default(line)

	def do_alarm(self, arguments):
		"""
		Set an alarm.

		To set an alarm, type in + (for alarms a certain time from now) or = (for
		alarms at a specific time), a time specification, and then a note to display
		at when that time has passed.

		The time specification can be a number of minutes (just a number), hours and
		minutes (in HH:MM format), days/hours/minutes (in DD-HH:MM format) or a full
		date (in YY/DD-HH:MM format).

		So an alarm an hour and a half from now could be done with 'alarm + 90 ...'
		or 'alarm + 1:30 ...', where ... is the note to display. An alarm at ten in 
		the evening would be 'alarm = 20:00'. An alarm 1 day from now would be done
		with 'alarm + 1-0:00'.
		"""
		# Parse the arguments.
		symbol, time_spec, note = arguments.split(None, 2)
		# Convert the time.
		if '-' in time_spec and '/' not in time_spec:
			time_spec = f'0/{time_spec}'
		try:
			time = gtime.Time.from_str(time_spec.replace(' ', '-'))
		except ValueError:
			print('I do not understand that time, master.')
			return
		# Set the alarm time.
		if symbol == '+':
			alarm = self.time + time
		else:
			if '/' not in time_spec:
				time.year = self.time.year
			if '-' not in time_spec:
				time.day = self.time.day
			alarm = time
		# Add the alarm to the alarm tracking.
		self.alarms.append((alarm, note))
		self.alarms.sort()
		# Update the user.
		print(f'Alarm set for {alarm}.')
		print(f'The next alarm is set for {self.alarms[0][0]} ({self.alarms[0][1]}).')

	def do_day(self, arguments):
		"""
		Advance the time by day increments.

		By default, the day command moves forward one day. If you provide an 
		integer argument, it instead moves forward that many days.

		The time is set to 6:00 in the morning on the next day.
		"""
		days = int(arguments) if arguments.strip() else 1
		self.time += gtime.Time(day = days)
		self.time.hour = 6
		self.time.minute = 0
		print(self.time)
		self.alarm_check('')

	def do_help(self, arguments):
		"""
		Handle help requests. (bool)

		Parameters:
		arguments: What to provide help for. (str)
		"""
		topic = arguments.lower()
		# check for aliases
		topic = self.aliases.get(topic, topic)
		# The help_text dictionary takes priority.
		if topic in self.help_text:
			print(self.help_text[topic].strip())
		# General help is given with no arguments.
		elif not topic:
			# Show the base help text.
			print(self.help_text['help'].strip())
			# Get the names of other help topics.
			names = [name[3:] for name in dir(self.__class__) if name.startswith('do_')]
			names.extend([name[5:] for name in dir(self.__class__) if name.startswith('help_')])
			names.extend(self.help_text.keys())
			# Clean up the names.
			names = list(set(names) - set(('debug', 'help', 'text')))
			names.sort()
			# Convert the names to cleanly wrapped text and output.
			name_lines = textwrap.wrap(', '.join(names), width = 79)
			if name_lines:
				print()
				print("Additional help topics available with 'help <topic>':")
				print('\n'.join(name_lines))
		# help_foo methods take priority over do_foo docstrings.
		elif hasattr(self, 'help_' + topic):
			help_method = getattr(self, 'help_' + topic)
			# Exit without pausing if requested by the help_foo method.
			if help_method():
				return True
		# Method docstrings are given for recognized commands.
		elif hasattr(self, 'do_' + topic):
			help_text = getattr(self, 'do_' + topic).__doc__
			help_text = textwrap.dedent(help_text).strip()
			print(help_text)
		# Display default text for unknown arguments.
		else:
			print("I can't help you with that.")

	def do_quit(self, arguments):
		"""Say goodbye to Egor."""
		return True

	def do_roll(self, arguments):
		"""
		Roll some dice. (r)

		The standard way to define a roll is nds, where n is the number of dice, and s
		is the number of sides each die has. So 3d6 rolls three six-sided dice. The n
		can be omitted if n = 1. So d20 rolls one twenty-sided die.

		You can end a roll specification with khm to keep the m highest dice, or klm 
		to keep the m lowest dice. So 2d20kl1 rolls two twenty-sided dice and keeps 
		the lowest one.

		You can start a roll specification with rx to repeat the roll r times. So
		6x3d6 rolls 3d6 six times. 6x4d6kh3 would be the standard way of rolling 
		ability scores.

		Note that you can type in a roll specification without the roll command and 
		Egor will still roll the dice. Egor likes rolling dice.
		"""
		try:
			print(dice.roll(arguments))
		except AttributeError:
			print("I don't know how to roll that, master.")

	def do_shell(self, arguments):
		"""Handle raw Python code. (!)"""
		print(eval(arguments))

	def do_srd(self, arguments):
		"""
		Search the Source Resource Document.

		The arguments are the terms you want to search by. If you just give some text,
		Egor tries to find that text with a case insensitive search. If you preced the
		terms with a $, it treats the rest of the argument as a regular expression, 
		and searches for that.

		Currently Egor only knows how to search for headers.
		"""
		# Search by regex or text as indicated.
		if arguments.startswith('$'):
			regex = re.compile(arguments[1:], re.IGNORECASE)
			matches = self.srd.header_search(regex)
		elif arguments.startswith('+'):
			regex = re.compile(arguments[1:], re.IGNORECASE)
			matches = self.srd.text_search(regex)
		else:
			matches = self.srd.header_search(arguments)
		if matches:
			# If necessary, get the player's choice of matches.
			if len(matches) == 1:
				choice = '1'
			else:
				for match_index, match in enumerate(matches, start = 1):
					print(f'{match_index}: {match.full_header()}')
				choice = input('\nWhich section would you like to view (return for none)? ')
			# Validate the choice.
			if choice:
				try:
					match = matches[int(choice) - 1]
				except (ValueError, IndexError):
					print('\nInvalid choice.')
				else:
					# Print the chosen section.
					print()
					print(match.full_text())
		else:
			# Warn the user if there are no matches.
			print('No matches found.')

	def do_time(self, arguments):
		"""
		Update the current game time. (t)

		Time can be specified as minutes, or has hour:minute. It is added to the
		current time, which is then displayed.

		The time specification can be preceded with 'set' or '=' to set the time
		to a value, rather than adding that value to the current time. You must
		put a space before the time value.

		With no arguments, this just displays the current time.
		"""
		# parse the arguments.
		words = arguments.split()
		if words:
			if words[0].lower() in ('set', '='):
				time_spec = words[1]
				reset = True
			else:
				time_spec = words[0]
				reset = False
			# Get the time.
			try:
				time = gtime.Time.from_str(time_spec)
			except ValueError:
				print('I do not understand that time, master.')
				return
			# Add or set as requested.
			if reset:
				self.time.hour = time.hour
				self.time.minute = time.minute
			else:
				self.time += time
		print(self.time)
		if words:
			self.alarm_check(time_spec)

	def onecmd(self, line):
		"""
		Interpret the argument. (str)

		Parameters:
		line: The line with the user's command. (str)
		"""
		# Catch errors and print the traceback.
		try:
			return super().onecmd(line)
		except:
			traceback.print_exc()

	def postcmd(self, stop, line):
		"""
		Post-command processing. (str)

		Parameters:
		stop: A flag for quitting the interface. (bool)
		line: The line with the user's command. (str)
		"""
		if not stop:
			print()
		return stop

	def precmd(self, line):
		"""
		Pre-command processing. (str)

		Parameters:
		line: The line with the user's command. (str)
		"""
		print()
		return line

	def preloop(self):
		"""Set up the interface. (None)"""
		# Load the SRD.
		self.srd = srd.SRD()
		# Set the default state.
		self.alarms = []
		self.time = gtime.Time(1, 1, 6, 0)
		# Formatting.
		print()

if __name__ == '__main__':
	egor = Egor()
	egor.cmdloop()
