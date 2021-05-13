"""
egor.py

A command line interface for a D&D DM helper.

Constants:
HELP_GENERAL: The general help text for Egor. (str)

Classes:
Egor: A helper for a D&D Dungeon master. (cmd.Cmd)
"""

import cmd
import collections
import re
import textwrap
import traceback

import dice
import srd
import gtime

HELP_GENERAL = """
You can use the roll command to roll dice, in all sorts of combinations. The
basic syntax is 'roll NdS' to roll N dice with S sides. See 'help roll' for 
more details and possibilities. Note that dice rolling is the default command,
and it can be done without using the command 'roll'.

Egor can track the in-game time for you. The time command can set and report
the current game time, and the day command can advance the time in day 
increments. You can also set alarms in game time to alert you of events that
should happen, using the alarm command.

You can store notes about the game with the note command, and later review them
with the study command. You can also search the Source Resource Documents with
the srd command.
"""

class Egor(cmd.Cmd):
	"""
	A helper for a D&D Dungeon master. (cmd.Cmd)

	Attributes:
	alarms: Alarms that have been set based on self.time. (list of tuple)
	changes: A flag for changes in the game state. (bool)
	srd: The stored Source Resource Document for D&D. (SRD)
	time: The current game time. (gtime.Time)

	Class Attributes:
	aliases: Different names for commands. (dict of str: str)
	help_text: Additional help text. (dict of str: str)
	tag_regex: A regular expression for note tags. (Pattern)
	time_vars: Variables for game time and alarms. (dict of str: str)

	Methods:
	alarm_check: Check for any alarms that should have gone off. (None)
	do_alarm: Set an alarm. (None)
	do_day: Advance the time by day increments. (None)
	do_note: Record a note. (None)
	do_quit: Exit the Egor interface. (True)
	do_roll: Roll some dice. (None)
	do_set: Set one of the options. (None)
	do_save: Save the current data. (None)
	do_srd: Search the Source Resource Document. (None)
	do_study: Study previously recorded notes. (None)
	do_time: Update the current game time. (None)
	load_data: Load any stored state data. (None)
	new_note: Store a note. (None)

	Overridden Methods:
	default
	do_help
	do_shell
	onecmd
	postcmd
	precmd
	preloop
	"""

	aliases = {'n': 'note', 'q': 'quit', 'r': 'roll', 't': 'time'}
	intro = 'Welcome, Master of Dungeons.\nI am Egor, allow me to assist you.\n'
	help_text = {}
	prompt = 'Yes, master? '
	tag_regex = re.compile(r'[a-zA-Z0-9\-]+')
	time_vars = {'combat': '10', 'long-rest': '8:00', 'room': '10', 'short-rest': '60'}

	def alarm_check(self, time_spec):
		"""
		Check for any alarms that should have gone off. (None)

		Parameters:
		time_spec: The user input that changed the time. (str)
		"""
		for alarm in self.alarms:
			alarm.check(time_spec, self.time)
		self.alarms = [alarm for alarm in self.alarms if not alarm.done]

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
		elif line.lower() in self.time_vars:
			self.do_time(line.lower())
		else:
			return super().default(line)

	def do_alarm(self, arguments):
		"""
		Set an alarm.
		
		The argument to the alarm command is an alarm specification, which has three
		parts: a symbol for the type of the alarm, a time specification, and then a 
		note to display when that time has passed.

		The three types and their symbols are:
			+ indicates a relative alarm, that will happen in a certain amount of 
				time.
			= indicates an absolute alarm, that will happen at a specific time.
			@ indicates a repeating alarm.

		The time specification can be a number of minutes (just a number), hours and
		minutes (in HH:MM format), days/hours/minutes (in DD-HH:MM format) or a full
		date (in YY/DD-HH:MM format). You can also use a time variable as a time
		specification.

		So an alarm an hour and a half from now could be done with 'alarm + 90 ...'
		or 'alarm + 1:30 ...', where ... is the note to display. An alarm at ten in 
		the evening would be 'alarm = 20:00'. An alarm 1 day from now would be done
		with 'alarm + 1-0:00'. An alarm that repeats every 30 minutes would be done
		with 'alarm @ 30'. One that repeats every short rest would be 'alarm @ 
		short-rest'. Note that repeating alarms must be a relative time value, or a
		time variable.

		As a special case you can use 'alarm kill'. This will list the current alarms
		and let you choose one to delete.
		"""
		if arguments.strip().lower() == 'kill':
			# Show the alarms.
			for alarm_index, alarm in enumerate(self.alarms, start = 1):
				print(f'{alarm_index}: {alarm}')
			# Get the user's choice.
			choice = input('\nWhich alarm would you like to kill, master (return for none)? ')
			if choice.strip():
				# Kill the alarm.
				del self.alarms[int(choice) - 1]
				print('\nIt squeaked when I killed it, master.')
		else:
			# Get the alarm
			try:
				alarm = gtime.new_alarm(arguments, self.time, self.time_vars)
			except ValueError:
				print('I do not understand that time, master.')
				return
			# Add it to the list.
			self.alarms.append(alarm)
			self.changes = True
			# Update the user.
			print(f'Alarm set for {alarm.trigger}.')

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
		self.changes = True
		self.alarm_check('day')

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

	def do_note(self, arguments):
		"""
		Record a note. (n)

		Write a note to yourself. Notes can later be read with the study command.

		At the end of your note you can put a pipe (|). Anything after the pipe is
		considered to be a tag. You can put in mutliple tags separated by anything 
		that isn't a letter, number, or dash (-). Tags can be used to search for 
		notes with the study command.
		"""
		self.new_note(arguments)
		self.changes = True
		print('Your note has been added to the scroll, master.')

	def do_quit(self, arguments):
		"""Say goodbye to Egor."""
		if self.changes:
			choice = input('But, master! The game state has changed! Shall I save it? ')
			if choice.lower() in ('yes', 'y', 'da'):
				self.do_save('')
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

	def do_save(self, arguments):
		"""Save the current data."""
		with open('dm.dat', 'w') as data_file:
			# Save the alarms.
			for alarm in self.alarms:
				data_file.write('alarm: {}\n'.format(alarm.data()))
			# Save the notes with tags (allows deleting notes w/o messing up tags).
			save_notes = [f'note: {note}' for note in self.notes]
			for tag, indices in self.tags.items():
				for index in indices:
					if '|' not in save_notes[index]:
						save_notes[index] += ' |'
					save_notes[index] += f' {tag}'
			for note in save_notes:
				data_file.write(note + '\n')
			# Save the time data.
			data_file.write('time: {}\n'.format(self.time.short()))
			for var, value in self.time_vars.items():
				data_file.write('time-var: {} {}\n'.format(var, value))
		self.changes = False
		print('I have stored all of the incantations, master.')

	def do_set(self, arguments):
		"""
		Set one of the options.

		The options you can set include:

		* time-var: Changes or adds time variables (see the time command). Follow
			time-var with a time variable name and a time specification, such as
			'set time-var short-rest 5'. Setting a time variable to another time
			variable does not work.
		"""
		option, setting = arguments.split(None, 1)
		option = option.lower()
		if option == 'time-var':
			variable, value = setting.split()
			variable = variable.lower()
			self.time_vars[variable] = value
			print(f'The time variable {variable} was set to {value}.')
			self.changes = True
		else:
			print(f'I do not recognize the option {option!r}, master.')

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

	def do_study(self, arguments):
		"""
		Study previously recorded notes.

		As an argument you can give a tag. Only notes with that tag will be
		displayed. Or you can give a dollar sign ($) followed by a regular
		expression. Any note matching that regular expression will be shown.
		Regular expressions are searched with the IGNORECASE flag.
		"""
		if not arguments.strip():
			# Show all notes.
			for note in self.notes:
				print(note)
		elif arguments.startswith('$'):
			# Subset notes with a regular expression.
			note_regex = re.compile(arguments[1:])
			for note in self.notes:
				if note_regex.search(note, re.IGNORECASE):
					print(note)
		else:
			# Subset notes with a tag.
			if arguments in self.tags:
				for note_index in self.tags[arguments]:
					print(self.notes[note_index])
			else:
				print(f'I do not know the tag {arguments!r}, master.')

	def do_time(self, arguments):
		"""
		Update the current game time. (t)

		Time can be specified as minutes, or has hour:minute. It is added to the
		current time, which is then displayed. There are also time variables that
		Egor recognizes. By default, these are 'short-rest' (60 minutes), long-rest
		(8 hours), combat (10 minutes), and room (10 minutes). You can change these
		values and create new time variables using the set command. Note that you
		can enter a time variable without the time command, and it will increment
		the time by that ammount.

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
				time = gtime.Time.from_str(self.time_vars.get(time_spec, time_spec))
			except ValueError:
				print('I do not understand that time, master.')
				return
			# Add or set as requested.
			if reset:
				self.time.hour = time.hour
				self.time.minute = time.minute
			else:
				self.time += time
			self.changes = True
		print(self.time)
		if words:
			self.alarm_check(time_spec)

	def load_data(self):
		"""Load any stored state data. (None)"""
		with open('dm.dat') as data_file:
			for line in data_file:
				tag, data = line.split(':', 1)
				if tag == 'alarm':
					self.alarms.append(gtime.Alarm.from_data(data.strip()))
				if tag == 'note':
					self.new_note(data.strip())
				elif tag == 'time':
					self.time = gtime.Time.from_str(data.strip())
				elif tag == 'time-var':
					var, value = data.split()
					self.time_vars[var] = value

	def new_note(self, note_text):
		"""
		Store a note. (None)

		Parameters:
		note_text: The note, possibly with tags. (str)
		"""
		note, pipe, tags = note_text.partition('|')
		self.notes.append(note)
		for tag in self.tag_regex.findall(tags):
			self.tags[tag].append(len(self.notes) - 1)

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
		self.changes = False
		self.time = gtime.Time(1, 1, 6, 0)
		self.time_vars = Egor.time_vars.copy()
		self.notes = []
		self.tags = collections.defaultdict(list)
		# Load any saved state.
		try:
			self.load_data()
			print('The game state has been restored, master.')
		except FileNotFoundError:
			pass
		# Formatting.
		print()

if __name__ == '__main__':
	egor = Egor()
	egor.cmdloop()
