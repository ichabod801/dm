"""
egor.py

A command line interface for a D&D DM helper.

Classes:
CreatureError: An error getting a creature. (ValueError)
Egor: A helper for a D&D Dungeon master. (cmd.Cmd)
"""

import cmd
import collections
import os
import random
import re
import textwrap
import time
import traceback

from . import creature
from . import dice
from . import gtime
from . import markdown
from . import text
from . import voice
from . import weather

class CreatureError(ValueError):
	pass

class Egor(cmd.Cmd):
	"""
	A helper for a D&D Dungeon master. (cmd.Cmd)

	Attributes:
	alarms: Alarms that have been set based on self.time. (list of tuple)
	auto_save: A flag for requesting a save every 30 minutes. (bool)
	campaign: The loaded campaign information. (SRD)
	campaign_folder: A path to the folder with the campaign files. (str)
	changes: A flag for changes in the game state. (bool)
	combatants: The creatures in the current combat. (dict of str: Creature)
	encounters: Preset encounters. (dict of str: tuple)
	init: The initiative order for the current combat. (list of Creature)
	init_count: The current actor in combat. (int)
	pcs: The player characters in the campaign. (dict of str: Creature)
	round: The number of the current combat round. (int)
	srd: The stored Source Resource Document for D&D. (SRD)
	time: The current game time. (gtime.Time)
	timer: A time checkpoint for autosaves. (float)
	zoo: The creatures loaded for combat. (dict of str: Creature)

	Class Attributes:
	aliases: Different names for commands. (dict of str: str)
	help_text: Additional help text. (dict of str: str)
	on_off_options: The options that are flags. (list of str)
	tag_regex: A regular expression for note tags. (Pattern)
	time_vars: Variables for game time and alarms. (dict of str: str)

	Methods:
	add_encounter: Add an encounter to the initiative tracking. (None)
	alarm_check: Check for any alarms that should have gone off. (None)
	combat_text: Print a summary of the current combat. (None)
	do_alarm: Set an alarm. (None)
	do_ac: Set the armor class modifier for a creature. (None)
	do_attack: Have the current combatant attack another one. (None)
	do_autoattack: Run all of the current combatants attacks with no target. (None)
	do_campaign: Search the campaign documents. (None)
	do_condition: Add a condition to a creature. (None)
	do_date: Give the date as specified by the campaign calendar. (None)
	do_day: Advance the time by day increments. (None)
	do_encounter: Create an encounter for a later combat. (None)
	do_heal: Heal a creature. (None)
	do_hit: Do damage to a creature. (None)
	do_hp: Set a creature's HP. (None)
	do_kill: Remove a creature from the initiative order. (None)
	do_name: Generate a random NPC name. (None)
	do_next: Show the next person in the initiative queue. (None)
	do_note: Record a note. (None)
	do_npc: Creates a full random NPC. (None)
	do_opportunity: Have the one combatant attack another one. (None)
	do_pc: Add or remove a player character. (None)
	do_personality: Generate a random personality. (None)
	do_quit: Exit the Egor interface. (True)
	do_repeat: Repeat a command multiple times. (None)
	do_roll: Roll some dice. (None)
	do_save: Have a creature make a saving throw. (None)
	do_set: Set one of the options. (None)
	do_skill: Have a creature make a skill check. (None)
	do_srd: Search the Source Resource Document. (None)
	do_stats: Show the full stat block for a given creature. (None)
	do_store: Save the current data. (None)
	do_study: Study previously recorded notes. (None)
	do_table: Roll on a table in the SRD or a campaign file. (None)
	do_time: Update the current game time. (None)
	do_uncondition: Remove a condition from a creature. (None)
	do_xp: Adjust the current experience point total. (None)
	get_combatants: Get additional combatants from the user. (None)
	get_creature: Get a creature to apply a command to. (Creature)
	get_encounter: Get an encounter from the user. (list)
	load_campaign: Load stored campaign data. (None)
	load_data: Load any stored state data. (None)
	markdown_search: Search a markdown document tree. (None)
	new_note: Store a note. (None)
	new_pc: Create a new entered player character. (None)
	set_initiative: Set up a new initiative order, including the PCs. (None)

	Overridden Methods:
	default
	do_help
	do_shell
	onecmd
	postcmd
	precmd
	preloop
	"""

	aliases = {'@': 'attack', '@@': 'autoattack', '&': 'note', '*': 'repeat', 'auto': 'autoattack', 
		'camp': 'campaign', 'con': 'condition', 'init': 'initiative', 'n': 'next', 'op': 'opportunity', 
		'q': 'quit', 'r': 'roll', 't': 'time', 'uncon': 'uncondition'}
	intro = 'Welcome, Master of Dungeons.\nI am Egor, allow me to assist you.\n'
	help_text = {'conditions': text.HELP_CONDITIONS, 'cover': text.HELP_SIGHT, 'help': text.HELP_GENERAL, 
		'sight': text.HELP_SIGHT}
	on_off_options = ('auto-attack', 'auto-kill', 'auto-save', 'average-hp', 'dex-tiebreak', 'group-hp', 
		'random-tiebreak')
	prompt = 'Yes, master? '
	tag_regex = re.compile(r'[a-zA-Z0-9\-]+')
	time_vars = {'combat': '10', 'long-rest': '8:00', 'room': '10', 'short-rest': '60'}

	def add_encounter(self, encounter):
		"""
		Add an encounter to the initiative tracking. (None)

		Parameters:
		encounter: An encounter specification from get_encounter. (list of tuple)
		"""
		for name, roll, group in encounter:
			data = self.zoo[name]
			count = dice.roll(roll)
			for bad_guy in range(count):
				if count > 1:
					sub_name = f'{name}-{bad_guy + 1}'
				else:
					sub_name = name
				npc = data.copy(sub_name)
				if not group:
					npc.init()
					self.init.append(npc)
				self.combatants[npc.name.lower()] = npc
			# Handle groups
			if group:
				sub_name = f'{name}-group-of-{count}'
				npc = data.copy(sub_name, average_hp = True)
				npc.init()
				self.init.append(npc)

	def alarm_check(self, time_spec):
		"""
		Check for any alarms that should have gone off. (None)

		Parameters:
		time_spec: The user input that changed the time. (str)
		"""
		for alarm in self.alarms:
			alarm.check(time_spec, self.time)
		self.alarms = [alarm for alarm in self.alarms if not alarm.done]

	def combat_text(self):
		"""Print a summary of the current combat. (None)"""
		if self.init_count == 0:
			print(self.voice['new-round'].format(self.round))
		print(self.init[self.init_count].combat_text())
		if self.auto_attack and not self.init[self.init_count].pc:
			print('-------------------')
			print(self.init[self.init_count].auto_attack())
		print('-------------------\n')
		by_number = list(enumerate((str(combatant) for combatant in self.init), start = 1))
		for index, combatant in by_number[(self.init_count + 1):] + by_number[:self.init_count]:
			print(f'{index}: {combatant}')

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

	def do_ac(self, arguments):
		"""
		Set the armor class modifier for a creature.

		Note that this does not change a creature's AC directly, it sets the 
		modifier to the creature's AC. So if Fred gets +2 bonus for two weapon
		fighting, you would use 'ac fred 2'.

		The arguments are the creature's name or initiative order, and the 
		value to set it's armor class modifier to.
		"""
		creature_id, ac_mod = arguments.split()
		creature = self.get_creature(creature_id)
		creature.ac_mod = int(ac_mod)
		total_ac = creature.ac + creature.ac_mod
		print(self.voice['new-ac'].format(creature.name, creature.ac, creature.ac_mod, total_ac))

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
			choice = input(self.voice['choose-alarm'])
			if choice.strip():
				# Kill the alarm.
				del self.alarms[int(choice) - 1]
				print(self.voice['removed-alarm'])
		else:
			# Get the alarm
			try:
				alarm = gtime.new_alarm(arguments, self.time, self.time_vars)
			except ValueError:
				print(self.voice['error-time'].format(arguments))
				return
			# Add it to the list.
			self.alarms.append(alarm)
			self.changes = True
			# Update the user.
			print(f'Alarm set for {alarm.trigger}.')

	def do_attack(self, arguments, attacker = None):
		"""
		Have the current combatant attack another one. (@)

		The first two arguments must be the name of the target and the name of the 
		attack. The target may be identified by their number in the initiative order.
		The attack may be identified by it's letter in the creature's attack section.
		If no attack is specified, the creature's first attack will be used. If any 
		optional arguments are used, the attack used must be specified.

		Advantage or disadvantage for the attack may be given by 'ad', 'advantage',
		'dis', or 'disadvantage' as an optional argument. Any numeric optional 
		argument will be treated as a temporary bonus or penalty to the attack roll.
		"""
		# Parse the attack and the target.
		words = arguments.split()
		target = words[0]
		attack = words[1] if len(words) > 1 else ''
		# Parse any optional arguments.
		advantage = 0
		bonus = 0
		for word in words[2:]:
			check = word.lower()
			if check in ('ad', 'advantage'):
				advantage = 1
			elif check in ('dis', 'disadvantage'):
				advantage = -1
			elif check.isdigit() or check[0] in ('+', '-') and check[1:].isdigit():
				bonus = int(check)
		# Get the creatures involved in the attack.
		target = self.get_creature(target, 'combat')
		if attacker is None:
			attacker = self.init[self.init_count]
		# Make the attack
		try:
			total, text = attacker.attack(target, attack, advantage, bonus)
		except ValueError:
			# Handle attack errors.
			print(self.voice['error-attack'].format(attacker.name, attack))
			print(self.voice['list-attacks'].format(attacker.name))
			for letter, attack in zip(creature.Creature.letters, attacker.attacks):
				print(f'   {letter}: {attack}')
		else:
			# Check for automatic kills.
			if target.hp == 0 and self.auto_kill and not target.pc:
				self.do_kill(target.name, quiet = True)
			print(text)

	def do_autoattack(self, arguments):
		"""
		Run all of the current combatants attacks with no target. (auto, @@)
		"""
		attacker = self.init[self.init_count]
		print(attacker.auto_attack())

	def do_autotag(self, arguments):
		"""
		Create automatic tags for every note.

		The arguments become tags added to every note. To turn autotags off, just 
		use autotag with no arguments. Setting autotags replaces any previous 
		autotags. Note that autotags are not saved when you quit from the Egor 
		system.
		"""
		self.auto_tag = arguments.strip()

	def do_campaign(self, arguments):
		"""
		Search the campaign documents. (camp)

		The arguments are the terms you want to search by. If you just give some text,
		Egor tries to find that header with a case insensitive search. If you preced 
		the terms with a $, it treats the rest of the argument as a regular 
		expression, and searches the document headers for that. If you precede it with 
		a +, it treats the rest of the argument as a regular expression, and searches 
		the document text for that
		"""
		self.markdown_search(arguments, self.campaign)

	def do_condition(self, arguments):
		"""
		Add a condition to a creature. (con)

		The arguments are a creature name or initiative order, and a condition to
		add to their condition list. An optional third argument is a number of 
		rounds they condition will last.
		"""
		words = arguments.split()
		target = self.get_creature(words[0], 'combat')
		condition = words[1].lower()
		if len(words) > 2:
			rounds = int(words[2])
		else:
			rounds = -1
		target.conditions[condition] = rounds
		print(self.voice['confirm-condition'].format(target.name, condition))

	def do_date(self, arguments):
		"""
		Give the date as specified by the campaign calendar. 

		You can specify a format name as the argument. Otherwise, you get the default 
		format for that calendar.
		"""
		# Process the format name argument.
		format_name = arguments.strip().lower()
		if not format_name:
			format_name = 'default'
		# Check for bad formats or no calendar.
		if self.campaign is None:
			print(self.voice['error-no-campaign'])
		elif self.campaign.calendar is None:
			print(self.voice['error-no-calendar'])
		elif format_name not in self.campaign.calendar.formats:
			print(self.voice['error-date-format'].format(arguments))
		else:
			# Print the date.
			print(self.campaign.calendar.date(self.time.day, format_name))

	def do_day(self, arguments):
		"""
		Advance the time by day increments.

		By default, the day command moves forward one day. If you provide an 
		integer argument, it instead moves forward that many days.

		The time is set to 6:00 in the morning on the next day.
		"""
		# Change the day.
		days = int(arguments) if arguments.strip() else 1
		last_year = self.time.year
		self.time += gtime.Time(day = days)
		# Check for year change.
		if last_year != self.time.year:
			self.campaign.calendar.set_year(self.time.year)
			gtime.Time.year_length = self.campaign.calendar.current_year['year-length']
		# Set to morning.
		self.time.hour = 6
		self.time.minute = 0
		# Update the user and the system tracking.
		print(self.time)
		self.changes = True
		self.alarm_check('day')

	def do_encounter(self, arguments):
		"""
		Create an encounter for a later combat.

		An encounter is just a set of creatures that you would otherwise enter at the
		start of a combat done with the initiatve command. Instead of entering them at
		that time, you use the & argument to the initiative command and enter in the
		encounter name.

		The argument to the encounter command is the name of the encounter you are
		creating.

		When giving a count of bad guys for an encounter, you can give a valid die 
		roll instead. Then when you use the encounter, the number of that bad guy will
		be randomly generated. 
		"""
		# Get the name of the encounter.
		name = arguments.strip()
		if not name:
			print(self.voice['error-enc-name'])
			return
		self.encounters[name] = []
		while True:
			# Get the monster.
			bad_guy = input(self.voice['choose-bad-guy']).strip()
			if not bad_guy:
				break
			#bad_guy = bad_guy.replace(' ', '-')
			if bad_guy not in self.zoo:
				print(self.voice['error-creature-enc'])
				continue
			# Get the number of monsters.
			# !! needs groups, do with one in the init, no number, all in combatants.
			count = input(self.voice['choose-bad-count']).lower()
			group = 'g' in count
			if group:
				count = count.replace('g', '')
			if count.strip():
				if not (count.isdigit() or dice.DICE_REGEX.match(count)):
					print(self.voice['error-bad-count'])
					continue
			else:
				count = 1
			self.encounters[name].append((bad_guy, count, group))
		self.changes = True

	def do_git(self, arguments):
		"""Egor doesn't understand git."""
		print(self.voice['error-git'])

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
				print(self.voice['more-help'])
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
			print(self.voice['error-help'])

	def do_heal(self, arguments):
		"""
		Heal a creature.

		The arguments are a creature name or initiative order number, and a number
		of points of healing for that creature. A die roll can be used for the points
		of healing.
		"""
		target_id, healing = arguments.split()
		target = self.get_creature(target_id)
		if dice.DICE_REGEX.match(healing):
			healing = dice.roll(healing)
			print(f'{healing} hp of damage was healed.')
		target.heal(int(healing))
		if target.hp_temp:
			print(self.voice['confirm-hp-temp'].format(target.name, target.hp, target.hp_temp))
		else:
			print(self.voice['confirm-hp'].format(target.name, target.hp))

	def do_hit(self, arguments):
		"""
		Do damage to a creature.

		The arguments are a creature name or initiative order number, and a number
		of points of damage to do to that creature. A die roll can be used for the
		points of damage.
		"""
		# Parse the arguments.
		target_id, damage = arguments.split()
		target = self.get_creature(target_id)
		# Apply the damage.
		if dice.DICE_REGEX.match(damage):
			damage = dice.roll(damage)
			print(f'{damage} hp of damage was dealt.')
		target.hit(int(damage))
		if target.hp_temp:
			print(self.voice['confirm-hp-temp'].format(target.name, target.hp, target.hp_temp))
		else:
			print(self.voice['confirm-hp'].format(target.name, target.hp))
		# Check for automatic kills.
		if target.hp == 0 and self.auto_kill and not target.pc:
			self.do_kill(target.name, quiet = True)

	def do_hp(self, arguments):
		"""
		Set a creature's hit points.

		The arguments are a creature name or initiative order number, and a number
		of points of damage to do to that creature. You can also give the optional
		argument of 'temp' or 'temporary' to set the creature's temporary hit points.
		"""
		# Parse the arguments.
		words = arguments.split()
		target = self.get_creature(words[0])
		# Apply the hp as directed.
		if len(words) > 2 and words[2].lower() in ('temp', 'temporary'):
			target.hp_temp = max(target.hp_temp, int(words[1]))
		else:
			target.hp = min(int(words[1]), target.hp_max)
		# Notify the user of the new state.
		if target.hp_temp:
			print(self.voice['confirm-hp-temp'].format(target.name, target.hp, target.hp_temp))
		else:
			print(self.voice['confirm-hp'].format(target.name, target.hp))

	def do_initiative(self, arguments):
		"""
		Start a combat by rolling initiative. (init)

		Using 'add' or '+' in the arguments means you want to add creatures to the
		current initiative. Using 'encounter' or '&' in the arguments means you
		wish to use a predefined encounter. You will be asked for the encounter's
		name if you choose this option. If you precede the name with $, the rest
		of the name will be treated as a regular expression. The encounter used
		will be randomly chosen from those who's name matches the regular expression.

		These must be separate words, so '&+' will not be recongized, but '& +'
		will be.

		You will be asked for the initiative for any PCs. If you do not enter a
		value, the system will roll the initiative for that character. This is 
		useful for NPCs.

		When entering a number of bad guys, you can add 'g' to the number. This will
		give one initiative to all of those bad guys. For example, if you enter in
		'wight' as the bad guy and '5g' as the number of bad guys, it will show up in
		the initiative as 'wight-group-of-5'. You can still get the individuals bad
		guys with 'wight-1' or 'wight-3'. If you try to target that group using their
		initiative order, you will be asked which particular one you want to hit.

		Note that by default, all creatures in a group have the same hit points, equal
		to the average hit points for that monster. Creatures not in a group each roll
		individual hit points. These hit point rolls/non-rolls can be changed by
		setting the average-hp and group-hp options with the set command.

		The default setting is to break initiative ties by dexterity score. This can
		be turned off with the dex-tiebreak option, and random tiebreaks (the 
		equivalent of rolling off with d20s) can be done with the random-tiebreak
		option.
		"""
		# Parse the arguments.
		arg_words = arguments.split()
		add = '+' in arg_words or 'add' in arg_words
		encounter_flag = '&' in arg_words or 'encounter' in arg_words
		# Check for the encounter (if it's random the DM will want to know who it is first)
		if encounter_flag:
			encounter = self.get_encounter()
			print('')
		# If you are not adding, set up the initiative and the PCs.
		if not add:
			self.set_initiative()
		# Get and add an encounter if requested.
		if encounter_flag:
			self.add_encounter(encounter)
		# Otherwise get the monsters from the DM.
		else:
			self.get_combatants()
		# Sort by the initiative rolls.
		if add:
			# Save the current point in combat, if adding to the combat.
			current = self.init[self.init_count]
			self.init.sort(key = self.init_sorter, reverse = True)
			self.init_count = self.init.index(current)
		else:
			self.init.sort(key = self.init_sorter, reverse = True)
		# Inform the DM of the initiative start.
		print()
		self.combat_text()

	def do_kill(self, arguments, quiet = False):
		"""
		Remove a creature from the initiative order.

		The argument is the name of the creature or it's order in the initiative.
		"""
		# Find the creature.
		creature = self.get_creature(arguments.lower(), 'combat')
		for death_index, living in enumerate(self.init):
			if living.name.lower() == creature.name.lower():
				break
		else:
			# Print a warning if you can't find the creature.
			print(self.voice['error-creature'].format(arguments))
			return
		# Remove the creature.
		del self.init[death_index]
		if death_index < self.init_count:
			self.init_count -= 1
		# Update the experience points.
		if self.xp_method == 'standard' and not creature.pc:
			self.xp += creature.xp
		# Show the current status.
		if quiet:
			print(self.voice['confirm-kill'].format(creature.name))
		else:
			self.combat_text()

	def do_name(self, arguments):
		"""
		Generate a random NPC name.

		There are two arguments to the name command: the culture/species of the name, 
		and the gender/type of the name. These are defined in the campaign documents,
		in the names chapter.
		"""
		culture, gender = arguments.split()
		try:
			# Print a random name.
			print(self.campaign.get_name(culture.lower(), gender.lower()))
		except KeyError:
			# Catch any errors, and clarify which part is the error.
			if culture in self.campaign.names:
				print(self.voice['error-gender'].format(culture, gender))
			else:
				print(self.voice['error-culture'].format(culture))

	def do_next(self, arguments):
		"""
		Show the next person in the initiative queue. (n)
		"""
		self.init_count += 1
		if self.init_count >= len(self.init):
			self.init_count = 0
			self.round += 1
		combatant = self.init[self.init_count]
		combatant.update_conditions()
		self.combat_text()

	def do_note(self, arguments):
		"""
		Record a note. (&)

		Write a note to yourself. Notes can later be read with the study command.

		At the end of your note you can put a pipe (|). Anything after the pipe is
		considered to be a tag. You can put in mutliple tags separated by anything 
		that isn't a letter, number, or dash (-). Tags can be used to search for 
		notes with the study command.
		"""
		if self.auto_tag:
			if '|' in arguments:
				arguments = f'{arguments} {self.auto_tag}'
			else:
				arguments = f'{arguments} | {self.auto_tag}'
		self.new_note(arguments)
		self.changes = True
		print(self.voice['confirm-note'])

	def do_npc(self, arguments):
		"""
		Creates a full random NPC.
		"""
		culture = random.choice(list(self.campaign.names.keys()))
		while culture == 'formats':
			culture = random.choice(list(self.campaign.names.keys()))
		gender = random.choice(list(self.campaign.names[culture]['formats'].keys()))
		self.do_name(f'{culture} {gender}')
		print(gender, culture, random.choice(text.CLASSES))
		print()
		self.do_personality('')

	def do_opportunity(self, arguments):
		"""
		Have the one combatant attack another one. (op)

		The first three arguments must be the name of the attacker, the name of the 
		target, and the name of the attack. The attacker and the target may be 
		identified by their number in the initiative order. The attack may be 
		identified by it's letter in the creature's attack section. If no attack is 
		specified, the creature's first attack will be used. If any optional arguments 
		are used, the attack used must be specified.

		Advantage or disadvantage for the attack may be given by 'ad', 'advantage',
		'dis', or 'disadvantage' as an optional argument. Any numeric optional 
		argument will be treated as a temporary bonus or penalty to the attack roll.

		This is basically the attack command, with the added first argument to identify
		the attacker. 
		"""
		words = arguments.split()
		attacker = self.get_creature(words[0], 'open')
		self.do_attack(' '.join(words[1:]), attacker)

	def do_pc(self, arguments):
		"""
		Add or remove a player character.

		The pc command takes two arguments. The first argument is either add or remove,
		depending on which you want to do. The second argument is the PC's name. When
		entering a PC, you will be asked further information about the PC stats and
		abilities.
		"""
		action, name = arguments.split(None, 1)
		low_name = name.strip().lower()
		if action == 'remove':
			if low_name in self.pcs:
				del self.pcs[low_name]
				print(self.voice['confirm-pc-rem'].format(name))
				self.changes = True
			else:
				print(self.voice['error-pc'].format(name))
		elif action == 'add':
			pc_data = [name]
			pc_data.append(input(self.voice['pc-init']))
			pc_data.append(input(self.voice['pc-ac']))
			pc_data.append(input(self.voice['pc-hp']))
			pc_data.append(input(self.voice['pc-abilities']))
			self.new_pc(pc_data)
		else:
			print(self.voice['error-pc-arg'].format(action))

	def do_personality(self, arguments):
		"""
		Generate a random personality.

		If called with no arguments, the personality command gives you a bond, a flaw,
		a goal, an ideal, and a trait. You can use any one of those as an argument to
		just get that type of personality characteristic. Or, you can use an integer
		argument to get that many characteristics from all types.
		"""
		arguments = arguments.strip().lower()
		# Handle full NPC traits.
		if not arguments:
			print(f'Bond: {random.choice(text.BONDS)}.')
			print(f'Flaw: {random.choice(text.FLAWS)}.')
			print(f'Goal: {random.choice(text.GOALS)}.')
			print(f'Ideal: {random.choice(text.IDEALS)}.')
			print(f'Trait: {random.choice(text.TRAITS)}.')
		# Handle specific NPC traits.
		elif arguments == 'bond':
			print(f'Bond: {random.choice(text.BONDS)}.')
		elif arguments == 'flaw':
			print(f'Flaw: {random.choice(text.FLAWS)}.')
		elif arguments == 'goal':
			print(f'Goal: {random.choice(text.GOALS)}.')
		elif arguments == 'ideal':
			print(f'Ideal: {random.choice(text.IDEALS)}.')
		elif arguments == 'trait':
			print(f'Trait: {random.choice(text.TRAITS)}.')
		# Handle general NPC traits.
		elif arguments.isdigit():
			all_traits = text.BONDS + text.FLAWS + text.GOALS + text.IDEALS + text.TRAITS
			print('\n'.join(random.choices(all_traits, k = int(arguments))))
		# Handle unknown NPC traits.
		else:
			print(self.voice['error-personality'])

	def do_quit(self, arguments):
		"""Say goodbye to Egor."""
		if self.changes:
			choice = input(self.voice['query-save'])
			if choice.lower() in text.YES:
				self.do_store('')
		return True

	def do_repeat(self, arguments):
		"""
		Repeat a command multiple times. (*)

		The arguments to the repeat command are a number and another command 
		(complete with the arguments for that command). The command specified in
		the second argument is repeated a number of times equal to the first
		argument. So 'repeat 3 attack Fred shortsword' does three attacks on Fred
		from the current combatant with their shortsword.
		"""
		count, command = arguments.split(None, 1)
		for repeat in range(int(count)):
			self.onecmd(command)

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
			print(self.voice['error-roll'])

	def do_save(self, arguments):
		"""
		Have a creature make a saving throw.

		The arguments are the name of the target, the ability for the save, and 
		the DC of the save. An optional fourth argument can specify advantage with
		'ad' or 'advantage' and disadvantage with 'dis' or 'disadvantage'.
		"""
		# Parse the arguments.
		words = arguments.split()
		target, ability, dc = words[:3]
		# Get the target.
		target = self.get_creature(target)
		# Check for dis/advantage.
		if len(words) > 3 and words[3].lower() in ('ad', 'advantage'):
			advantage = 1
		elif len(words) > 3 and words[3].lower() in ('dis', 'disadvantage'):
			advantage = -1
		else:
			advantage = 0
		# Make the roll.
		roll, success = target.save(ability[:3], int(dc), advantage)
		# Report the results.
		if success:
			print(self.voice['success-save'].format(target.name, roll))
		else:
			print(self.voice['failure-save'].format(target.name, roll))

	def do_set(self, arguments):
		"""
		Set one of the options.

		The options you can set include:
		
		* auto-attack: If set to true/1/yes, Egor automatically makes all of each
			combatant's attacks when it is their turn in initiative.
		* auto-kill: If set to true/1/yes, Egor automatically removes non-pc
			creatures from the initiative order when they hit 0 hp. If set to
			false/0/no, you must manually remove them with the kill command.
		* auto-save: If set to true/1/yes, Egor asks you every thirty minutes if he
			he should save the current data.
		* average-hp: Assigns the average hit points to all non-PC creatures in the
			initiative order.
		* campaign: Sets the campaign folder and loads any markdown files from that
			folder that start with two digits and a period (.).
		* climate: Sets the default climate for the weather command.
		* group-hp: Assigns the average hit points to all members of groups in the
			initiative order.
		* season: Sets the default season for the weather command.
		* time-var: Changes or adds time variables (see the time command). Follow
			time-var with a time variable name and a time specification, such as
			'set time-var short-rest 5'. Setting a time variable to another time
			variable does not work.
		* voice: Changes the phrases used by the system. Can be 'dry' or 'egor'.
		* weather-roll: Sets the roll for how extreme high and low temperatures are.
		* xp-method: If this is set to 'standard', xp is generated from monsters
			base on CR. Otherwise, all xp comes from the xp command.
		"""
		option, setting = arguments.split(None, 1)
		option = option.lower()
		if option in self.on_off_options:
			attr = option.replace('-', '_')
			if setting.strip() in text.YES:
				setattr(self, attr, True)
				print(self.voice['confirm-on'].format(option))
			elif setting.strip() in text.NO:
				setattr(self, attr, False)
				print(self.voice['confirm-off'].format(option))
			else:
				print(self.voice['error-on-off'].format(option))
				return
			self.changes = True
		elif option == 'campaign':
			self.campaign_folder = setting
			self.load_campaign()
			print(self.voice['confirm-campaign'].format(self.campaign_folder))
			self.changes = True
		elif option == 'climate':
			if setting.lower() in weather.WEATHER_DATA:
				self.climate = setting.lower()
				print(self.voice['confirm-climate'])
				self.changes = True
			else:
				print(self.voice['error-climate'].format(setting))
		elif option == 'season':
			if setting.lower() in ('spring', 'summer', 'winter', 'fall'):
				self.season = setting.lower()
				print(self.voice['confirm-season'].format(self.season))
				self.changes = True
			else:
				print(self.voice['error-season'].format(setting))
		elif option == 'time-var':
			variable, value = setting.split()
			variable = variable.lower()
			self.time_vars[variable] = value
			print(self.voice['confirm-time-var'].format(variable, value))
			self.changes = True
		elif option == 'voice':
			try:
				self.voice = getattr(voice, setting.upper())
			except AttributeError:
				print(self.voice['error-voice'].format(setting))
			else:
				print(self.voice['confirm-voice'])
				self.prompt = self.voice['prompt']
				self.changes = True
		elif option == 'weather-roll':
			try:
				dice.roll(setting)
			except:
				print(self.voice['error-roll'])
			else:
				self.weather_roll = setting.lower()
				print(self.voice['confirm-weather'].format(self.weather_roll))
				self.changes = True
		elif option == 'xp-method':
			self.xp_method = setting.strip().lower()
		else:
			print(self.voice['error-option'].format(option))

	def do_shell(self, arguments):
		"""Handle raw Python code. (!)"""
		print(eval(arguments))

	def do_show(self, arguments):
		"""Show the initiative order."""
		self.combat_text()

	def do_skill(self, arguments):
		"""
		Have a creature make a skill check.

		The arguments are the name of the creature and the skill to roll the
		check for. You can also add a three letter ability abbreviation (such
		as str, dex, con, int, wis, or cha) to force the skill check to use a
		non-standard ability. You may use 'ad' or 'advantage' to do the check
		with advantage, or 'dis'/'disadvantage' to do the check at disadvantage.
		If you add 'pass' or 'passive', the result will also show the creature's
		passive score in that skill.

		If 'pcs' is given as the creature, the skill is rolled for all player
		characters.

		If no skill is given, or Egor does not recognize the skill, he will ask
		what skill should be checked.
		"""
		# Get the creature.
		words = arguments.split()
		if words[0].lower() == 'pcs':
			targets = list(self.pcs.values())
		else:
			targets = [self.get_creature(words[0])]
		# Set the default values.
		advantage = 0
		skill = ''
		ability = ''
		passive = False
		# Parse the arguments.
		for word in words[1:]:
			word = word.lower()
			# Check for dis/advantage.
			if word in ('ad', 'advantage'):
				advantage = 1
			elif word in ('dis', 'disadvantage'):
				advantage = -1
			# Check for noting passive.
			elif word in ('pass', 'passive'):
				passive = True
			# Check for known skills.
			elif word in creature.Creature.skill_abilities:
				skill = word
			# Check for abilities.
			elif word in ('str', 'dex', 'con', 'int', 'wis', 'cha'):
				ability = word
		# Ask for the skill in no recognized skill was in the arguments.
		if not skill:
			skills = list(creature.Creature.skill_abilities.keys())
			skills.sort()
			for skill_index, skill in enumerate(skills, start = 1):
				print(f'{skill_index}: {skill}')
			choice = input(self.voice['choose-skill'])
			skill = skills[int(choice)]
			print()
		# Make the skill check.
		for target in targets:
			roll, check = target.skill_check(skill, advantage, ability)
			if passive:
				passive_check = 10 + target.skills[skill] + 5 * advantage
				print(self.voice['confirm-passive'].format(target.name, roll, check, passive_check))
			else:
				print(self.voice['confirm-skill'].format(target.name, roll, check))

	def do_srd(self, arguments):
		"""
		Search the Source Resource Document.

		The arguments are the terms you want to search by. If you just give some text,
		Egor tries to find that header with a case insensitive search. If you preced 
		the terms with a $, it treats the rest of the argument as a regular 
		expression, and searches the document headers for that. If you precede it with 
		a +, it treats the rest of the argument as a regular expression, and searches 
		the document text for that
		"""
		self.markdown_search(arguments, self.srd)

	def do_stats(self, arguments):
		"""
		Show the full stat block for a given creature.

		The argument is the name of a creature or the creature's initiative order. If
		no argument is given, it returns the stat block for the currently acting
		creature in combat.
		"""
		if not arguments.strip():
			arguments = str(self.init_count + 1)
		creature = self.get_creature(arguments)
		print(creature.stat_block())

	def do_store(self, arguments):
		"""Save the current data."""
		# Save the application data.
		with open(os.path.join(self.location, 'dm.dat'), 'w') as data_file:
			# Save the on/off settings.
			for option in self.on_off_options:
				attr = option.replace('-', '_')
				data_file.write('{}: {}\n'.format(option, getattr(self, attr)))
			# Save the loaded campaign, if any.
			if self.campaign_folder:
				data_file.write('campaign: {}\n'.format(self.campaign_folder))
			# Save the system voice.
			data_file.write('voice: {}\n'.format(self.voice['__name__']))
		# Determine where the campaign data should be stored.
		if self.campaign_folder:
			path = os.path.join(self.location, self.campaign_folder, 'camp.dat')
			mode = 'w'
		else:
			path = os.path.join(self.location, 'dm.dat')
			mode = 'a'
		# Store the campaign specific data.
		with open(path, mode) as data_file:
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
			# Save any encounters.
			if self.encounters:
				for name, bad_guys in self.encounters.items():
					bad_texts = [f'{name}, {count}, {group}' for name, count, group in bad_guys]
					enc_text = 'encounter: {} = {}\n'.format(name, '; '.join(bad_texts))
					data_file.write(enc_text)
			# Save the weather data.
			data_file.write('climate: {}\n'.format(self.climate))
			data_file.write('season: {}\n'.format(self.season))
			data_file.write('weather-roll: {}\n'.format(self.weather_roll))
			# Save the experience points.
			data_file.write('xp: {}\n'.format(self.xp))
			data_file.write('xp-method: {}\n'.format(self.xp_method))
			# Save any pc mock ups created in the interface.
			for pc_data in self.pc_data.values():
				data_file.write('pc-data: {}\n'.format('; '.join(pc_data)))
		# Clean up.
		self.changes = False
		print(self.voice['confirm-store'])

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
				print(self.voice['error-tag'].format(arguments))

	def do_table(self, arguments):
		"""
		Roll on a table in the SRD or a campaign file.

		The argument to the table command is the name of the table. If you start the
		name with '$', the rest of the name is treated as a regular expression for 
		searching the known table names. You can also use 'list' as an argument to 
		list all tables in the system.
		"""
		# Parse the name.
		name = arguments.strip().lower()
		# Handle simple calls by name.
		if name in self.tables:
			print(self.tables[name].roll())
		# Handle calls using a regular expression.
		elif name.startswith('$'):
			regex = re.compile(name[1:])
			names = [name for name in self.tables.keys() if regex.search(name)]
			# Choose a single result.
			if len(names) == 1:
				table = names[0]
			# Get the user's choice for mutliple results.
			elif names:
				for name_index, name in enumerate(names, start = 1):
					print(f'{name_index}: {name.title()}')
				choice = input(self.voice['choose-table'])
				table = names[int(choice) - 1]
				print()
			# Warning the user if there were no results.
			else:
				print(self.voice['error-table-regex'])
				return
			# Print the result.
			print(self.tables[table].roll())
		# Handle requests for a list of tables.
		elif name == 'list':
			names = [name.title() for name in self.tables.keys()]
			names.sort()
			print('\n'.join(names))
		# Handle unknown tables.
		else:
			print(self.voice['error-table'].format(arguments))
			print(self.voice['more-tables'])

	def do_test(self, arguments):
		"""
		Test code used during development. (None)
		"""
		if arguments == 'monsters':
			self.zoo = {}
			sizes = ('*Tiny', '*Smal', '*Medi', '*Larg', '*Huge', '*Garg')
			search = [self.srd.chapters['monsters'], self.srd.chapters['creatures'], self.srd.chapters['npcs']]
			while search:
				node = search.pop()
				if node.level < 4:
					intro = node.children[0]
					if isinstance(intro, markdown.TextNode) and intro.lines[0][:5] in sizes:
						print(intro.parent)
						monster = creature.Creature(node)
						self.zoo[monster.name] = monster
					elif node.level < 3:
						search = [kid for kid in node.children if isinstance(kid, markdown.HeaderNode)] + search

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
				print(self.voice['error-time'].format(time_spec))
				return
			# Add or set as requested.
			last_year = self.time.year
			if reset:
				self.time.hour = time.hour
				self.time.minute = time.minute
			else:
				self.time += time
			self.changes = True
			# Check for year change.
			if last_year != self.time.year:
				self.campaign.calendar.set_year(self.time.year)
				gtime.Time.year_length = self.campaign.calendar.current_year['year-length']
		print(self.time)
		if words:
			self.alarm_check(time_spec)

	def do_uncondition(self, arguments):
		"""
		Remove a condition from a creature. (con)

		The arguments are a creature name or initiative order, and a condition to
		remove from their condition list.
		"""
		words = arguments.split()
		target = self.get_creature(words[0], 'combat')
		condition = words[1].lower()
		if condition in target.conditions:
			del target.conditions[condition]
			print(self.voice['confirm-uncondition'].format(target.name, condition))
		else:
			print(self.voice['error-uncondition'].format(target.name, condition))

	def do_weather(self, arguments):
		"""
		Generate random weather.

		The arguments to the weather command are the climate and the season. If you
		provide no arguments, it will use the default climate and season. The defaults
		start as temperate and spring, but you can change them with the set command.
		You can also set the temperature roll, which determines how variable the high
		and low temperatures are.

		Available climates include: cold-arid (not quite desert), cold-desert, 
		continental (south Canada/centra Asia), hot-arid, hot-desert, ice-cap,
		mediterranean, monsoon, oceanic (Pacific Northwest), rainforest, sub-arctic
		(colder continental), sub-polar (colder temperate), sub-tropical, temperate,
		and tudra.
		"""
		# Parse the arguments.
		if arguments.strip():
			climate, season = [word.lower() for word in arguments.split()]
		else:
			climate, season = self.climate, self.season
		# Get and print the weather messages.
		try:
			temp_low, temp_high, message = weather.temperature(climate, season, self.weather_roll)
			print(message)
			print(weather.wind())
			print(weather.precipitation(climate, season, temp_low, temp_high))
		except KeyError:
			if season in ('spring', 'summer', 'fall', 'winter'):
				print(self.voice['error-culture'].format(climate))
			else:
				print(self.voice['error-season'].format(season))

	def do_xp(self, arguments):
		"""
		Adjust the current experience point total.

		With an integer argument, that argument is added to the current xp total.
		With no argument it just displays the current xp total. With the argument
		'award' it calculates how much xp each player character gets, and resets the
		total to 0.
		"""
		try:
			self.xp += int(arguments)
		except ValueError:
			if arguments.strip().lower() == 'award':
				award = int(self.xp / len(self.pcs))
				self.xp = 0
				print(self.voice['xp-award'].format(award))
			elif arguments.strip():
				print(self.voice['error-xp'])
			else:
				print(self.voice['confirm-xp'].format(self.xp))
		else:
			print(self.voice['confirm-xp'].format(self.xp))

	def get_combatants(self):
		"""Get additional combatants from the user. (None)"""
		while True:
			# Get the monster.
			name = input(self.voice['choose-bad-guy']).strip()
			if not name:
				break
			name = name.replace(' ', '-')
			# Get the number of monsters.
			count = input(self.voice['choose-bad-count']).lower()
			# Check for groups.
			if 'g' in count:
				group = True
				count = count.replace('g', '')
			else:
				group = False
			# Parse the count.
			if count.strip():
				count = int(count)
			else:
				count = 1
			# Find the monster's stats.
			if name.lower() in self.zoo:
				data = self.zoo[name.lower()]
			else:
				# Ask for the initiative bonus if you can't find it.
				init = input(self.voice['set-init-bonus'].format(name))
				if init.strip():
					data = creature.Creature(markdown.HeaderNode(f'# {name}'))
					data.init_bonus = int(init)
				else:
					continue
			# Create and roll initiative for the bad guys.
			average_hp = self.average_hp or (group and self.group_hp)
			for bad_guy in range(count):
				# Number the bad guys if there's more than one.
				if count > 1:
					sub_name = f'{name}-{bad_guy + 1}'
				else:
					sub_name = name
				npc = data.copy(sub_name, average_hp)
				if not group:
					npc.init()
					self.init.append(npc)
				self.combatants[npc.name.lower()] = npc
			# Handle groups
			if group:
				sub_name = f'{name}-group-of-{count}'
				npc = data.copy(sub_name, average_hp = True)
				npc.init()
				self.init.append(npc)

	def get_creature(self, creature_text, context = 'open'):
		"""
		Get a creature to apply a command to. (Creature)

		If context is not 'open', only the current combatants are searched, by name or
		number.

		Parameters:
		creature_text: The identifier of the creature. (str)
		context: How narrow/broad the search should be. (str)
		"""
		creature = creature_text.strip().lower().replace(' ', '-')
		# Check the combat containers
		if creature in self.combatants:
			creature = self.combatants[creature.lower()]
		elif creature.isdigit():
			try:
				creature = self.init[int(creature) - 1]
			except ValueError:
				raise CreatureError(self.voice['error-creature-ndx'])
		# Check non-combat containers outside of combat.
		elif context == 'open' and creature in self.pcs:
			creature = self.pcs[creature.lower()]
		elif context == 'open' and creature in self.zoo:
			creature = self.zoo[creature.lower()]
		# Warn on not finding the creature.
		else:
			raise CreatureError(self.voice['error-creature'].format(creature_text))
		# Handle ids within groups.
		if 'group-of' in creature.name:
			count = creature.name.split('-')[-1]
			name = creature.name[:creature.name.index('-group')]
			which = input(self.voice['query-creature'].format(name, count))
			creature = self.get_creature(f'{name}-{which}')
		return creature

	def get_encounter(self):
		"""
		Get an encounter from the user and confirm the creatures in it. (list)

		The return value is a list of the creatures in the encounter, each represented
		by a tuple of their name, the number of that creature, and if it should be 
		treated as a group.
		"""
		enc_name = input(self.voice['choose-encounter'])
		if enc_name[0] == '$':
			enc_re = re.compile(enc_name[1:])
			possible = [name for name in self.encounters if enc_re.match(name)]
			if possible:
				enc_name = random.choice(possible)
			else:
				print(self.voice['error-enc-regex'])
				return
		else:
			enc_name = enc_name.strip().lower()
		print(self.voice['confirm-encounter'])
		encounter = []
		for name, roll, group in self.encounters[enc_name]:
			count = dice.roll(roll)
			print(f'{count}x {name}')
			encounter.append((name, str(count), group))
		return encounter

	def init_sorter(self, char):
		"""
		Sort function for character initiative. (tuple)

		Parameters:
		char: The character to be sorted. (Creature)
		"""
		init = char.initiative
		dex = char.abilities['dex'] if self.dex_tiebreak else 0
		rando = random.random() if self.random_tiebreak else 0
		return (init, dex, rando)

	def load_campaign(self):
		"""Load stored campaign data. (None)"""
		self.campaign = markdown.SRD(os.path.join(self.location, self.campaign_folder))
		self.tables = self.srd.tables.copy()
		self.tables.update(self.campaign.tables)
		self.zoo = self.srd.zoo.copy()
		self.zoo.update(self.campaign.zoo)
		self.pcs = self.campaign.pcs
		if self.campaign.calendar:
			self.campaign.calendar.set_year(self.time.year)
			gtime.Time.year_length = self.campaign.calendar.current_year['year-length']

	def load_data(self):
		"""Load any stored state data. (None)"""
		# Load the general application data.
		with open(os.path.join(self.location, 'dm.dat')) as data_file:
			for line in data_file:
				tag, data = line.split(':', 1)
				if tag == 'campaign':
					self.campaign_folder = data.strip()
				elif tag == 'voice':
					self.voice = getattr(voice, data.strip().upper())
					self.prompt = self.voice['prompt']
				elif tag in self.on_off_options:
					attr = tag.replace('-', '_')
					setattr(self, attr, data.strip() == 'True')
		# Determine where any campaign data is stored.
		if self.campaign_folder:
			path = os.path.join(self.location, self.campaign_folder, 'camp.dat')
		else:
			path = os.path.join(self.location, 'dm.dat')
		# Load the campaign specific data.
		with open(path) as data_file:
			for line in data_file:
				tag, data = line.split(':', 1)
				if tag == 'alarm':
					self.alarms.append(gtime.Alarm.from_data(data.strip()))
				elif tag == 'climate':
					self.climate = data.strip()
				elif tag == 'encounter':
					name, bad_guys = data.split('=')
					name = name.strip()
					bad_texts = bad_guys.split(';')
					self.encounters[name] = []
					for text in bad_texts:
						bad_name, count, group = text.split(',')
						group = group.strip().lower() == 'True'
						self.encounters[name].append((bad_name.strip(), count.strip(), group))
				elif tag == 'note':
					self.new_note(data.strip())
				elif tag == 'pc-data':
					pc_data = tuple(word.strip() for word in data.split(';'))
					self.new_pc(pc_data)
				elif tag == 'season':
					self.season = data.strip()
				elif tag == 'time':
					self.time = gtime.Time.from_str(data.strip())
				elif tag == 'time-var':
					var, value = data.split()
					self.time_vars[var] = value
				elif tag == 'weather-roll':
					self.weather_roll = data.strip()
				elif tag == 'xp':
					self.xp = int(data)
				elif tag == 'xp-method':
					self.xp_method = data.strip()

	def markdown_search(self, arguments, document):
		"""
		Search a markdown document tree. (None)

		Parameters:
		arguments: The user's search terms. (str)
		document: The document to search. (HeaderNode)
		"""
		# Search by regex or text as indicated.
		if arguments.startswith('$'):
			regex = re.compile(arguments[1:], re.IGNORECASE)
			matches = document.header_search(regex)
		elif arguments.startswith('+'):
			regex = re.compile(arguments[1:], re.IGNORECASE)
			matches = document.text_search(regex)
		else:
			matches = document.header_search(arguments)
		if matches:
			# If necessary, get the player's choice of matches.
			if len(matches) == 1:
				choice = '1'
			else:
				for match_index, match in enumerate(matches, start = 1):
					print(f'{match_index}: {match.full_header()}')
				choice = input(self.voice['choose-section'])
			# Validate the choice.
			if choice:
				try:
					match = matches[int(choice) - 1]
				except (ValueError, IndexError):
					print(self.voice['error-choice'])
				else:
					# Print the chosen section.
					print()
					print(match.full_text())
		else:
			# Warn the user if there are no matches.
			print(self.voice['error-match'])

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

	def new_pc(self, pc_data):
		"""
		Create a new entered player character. (None)

		Parameters:
		new_pc: The pc data from the user or stored data. (list of str)
		"""
		# Create a base creature with any specified abilities.
		lines = [f'# {pc_data[0]}']
		if pc_data[4].strip():
			lines.append('| STR')
			lines.append('| {}'.format(pc_data[4].replace(',', '|')))
		pc = creature.Creature(markdown.HeaderNode('\n'.join(lines)))
		pc.pc = True
		# Set the initiative bonus.
		if pc_data[1].strip():
			pc.init_bonus = int(pc_data[1])
		else:
			pc.init_bonus = pc.bonuses['dex']
		# Set the armor class.
		if pc_data[2].strip():
			pc.ac = int(pc_data[2])
		else:
			pc.ac = 10 + pc.bonuses['dex']
		# Set the hit points.
		if pc_data[3].strip():
			pc.hp = int(pc_data[3])
			pc.hp_max = pc.hp
		# Add the pc to the data tracking.
		key = pc.name.lower().replace(' ', '-')
		self.pcs[key] = pc
		self.pc_data[key] = pc_data
		self.changes = True

	def onecmd(self, line):
		"""
		Interpret the argument. (str)

		Parameters:
		line: The line with the user's command. (str)
		"""
		# Catch errors and print the traceback.
		try:
			return super().onecmd(line)
		except CreatureError as err:
			print(err.args[0])
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
		if time.time() - self.timer > 1800 and self.changes and self.auto_save:
			print(self.voice['alert-time'])
			choice = input(self.voice['query-save'])
			if choice.lower() in text.YES:
				self.do_store('')
			print()
			self.timer = time.time()
		return line

	def preloop(self):
		"""Set up the interface. (None)"""
		# Load the SRD.
		self.location = os.path.dirname(os.path.abspath(__file__))
		self.srd = markdown.SRD(os.path.join(self.location, 'srd'))
		self.tables = self.srd.tables.copy()
		self.zoo = self.srd.zoo.copy()
		# Set the default state.
		self.alarms = []
		self.auto_attack = False
		self.auto_kill = True
		self.auto_save = True
		self.auto_tag = ''
		self.average_hp = False
		self.campaign_folder = ''
		self.climate = 'temperate'
		self.combatants = {}
		self.dex_tiebreak = True
		self.group_hp = True
		self.encounters = {}
		self.init = []
		self.notes = []
		self.pc_data = {}
		self.pcs = {}
		self.random_tiebreak = False
		self.season = 'spring'
		self.time = gtime.Time(1, 1, 6, 0)
		self.time_vars = Egor.time_vars.copy()
		self.timer = time.time()
		self.tags = collections.defaultdict(list)
		self.voice = voice.EGOR
		self.weather_roll = '1d4*10'
		self.xp = 0
		self.xp_method = 'standard'
		# Load any saved state.
		try:
			self.load_data()
			print(self.voice['confirm-load'])
		except FileNotFoundError:
			pass
		if self.campaign_folder:
			self.load_campaign()
			# Restore any overwritten pcs.
			for pc_data in self.pc_data.values():
				self.new_pc(pc_data)
		# Track changes.
		self.changes = False
		# Formatting.
		print()

	def set_initiative(self):
		"""Set up a new initiative order, including the PCs. (None)"""
		self.init = []
		self.combatants = self.pcs.copy()
		self.init_count = 0
		self.round = 1
		# Get initiative for the PCs.
		for name, pc in self.combatants.items():
			init = input(self.voice['set-init'].format(name.capitalize()))
			# Roll initiative if none given.
			if init.strip():
				pc.initiative = int(init)
			else:
				pc.init()
			self.init.append(pc)

if __name__ == '__main__':
	egor = Egor()
	egor.cmdloop()
