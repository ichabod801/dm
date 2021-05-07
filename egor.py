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

import srd

HELP_GENERAL = """
There is no functionality, so there is no help.
"""

class Egor(cmd.Cmd):
	"""
	A helper for a D&D Dungeon master. (cmd.Cmd)

	Class Attributes:
	aliases: Different names for commands. (dict of str: str)
	help_text: Additional help text. (dict of str: str)

	Methods:
	do_quit: Exit the Egor interface. (True)
	do_srd: Search the Source Resource Document. (None)

	Overridden Methods:
	default
	do_help
	onecmd
	postcmd
	precmd
	preloop
	"""

	aliases = {'q': 'quit'}
	intro = 'Welcome, Master of Dungeons.\nI am Egor, allow me to assist you.\n'
	help_text = {}
	prompt = 'Yes, master? '

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
		else:
			return super().default(line)

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
		else:
			matches = self.srd.header_search(arguments)
		if matches:
			# If necessary, get the player's choice of matches.
			if len(matches) == 1:
				match = matches[0]
			else:
				for match_index, match in enumerate(matches, start = 1):
					print(f'{match_index}: {match.full_header()}')
				choice = input('\nWhich section would you like to view (return for none)? ')
			# Validate the choice.
			if choice:
				try:
					match = matches[int(match_index) - 1]
				except (ValueError, IndexError):
					print('\nInvalid choice.')
				else:
					# Print the chosen section.
					print()
					print(match.full_text())
		else:
			# Warn the user if there are no matches.
			print('No matches found.')

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
		# Formatting.
		print()

if __name__ == '__main__':
	egor = Egor()
	egor.cmdloop()
