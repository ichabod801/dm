"""
egor.py

A command line interface for a D&D DM helper.

Constants:
HELP_CONDITIONS: Summaries of the various conditions. (str)
HELP_GENERAL: The general help text for Egor. (str)

Classes:
Egor: A helper for a D&D Dungeon master. (cmd.Cmd)
"""

import cmd
import collections
import random
import re
import textwrap
import traceback

import creature
import dice
import srd
import gtime

HELP_CONDITIONS = """
Blinded: Can't see, fails all checks requiring sight, attacks have dis-
   advantage, attacks against have advantage.
Charmed: Can't attack the charmer or target them with harmul effects, charmer
   has advantage on social interactions with creature.
Deafened: Can't hear, fails all checks requiring hearing.
Exhausted: Depends on level of exhaustion:
   1. Disadvantage on ability checks.
   2. Speed halved.
   3. Disadvantage on attacks and saves.
   4. HP maximum is halved.
   5. Speed is reduced to 0.
   6. Dead.
Frightened: Disadvantage on ability checks and attacks while they can see the
   source of their fear, can't willing move close to the fear source.
Grappled: Speed = 0, can't benefit from bonus to speed. Ends if grappler is
   incapacitated, or if target is removed from grappler's reach.
Incapacitated: Cannot take actions or reactions.
Invisible: Can't be seen without special effect, counts as heavily obscured.
   The creature's location can be determined by noise and tracks. Attacks
   against have disadvantage, attacks have advantage.
Paralyzed: Incapacitated, can't move or speak, fails all str and dex saves,
   attacks against have advantage, hits are crits if within five feet.
Petrified: Weight increases by 10, stops aging, incapacitated, can't move or
   speak, is unaware of it's surroundings, attacks against have advantage,
   fails all str and dex saves, resistance to all damage, immune to poison
   and disease (although current poison/disease is just suspended).
Poisoned: Disadvantage on attacks and ability checks.
Prone: May crawl or stand up, disadvantage on attacks, attacks have advantage
   if the attacker is within 5 ft., disadvantage otherwise.
Restrained: Speed = 0, can't benefit from bonus to speed, attacks against have
   advantage, attacks have disadvantage, disadvantage on dex saves.
Stunned: Incapacitated, can't move, and has limited speech. Fails all dex and
   str saves, attacks against have advantage.
Unconcious: Incapacitated, can't move or speak, is unaware of it's surround-
   ings, drops what it is holding, falls prone, fails all dex and str saves,
   attacks against have advantage, any attack is a crit if within 5 ft.
"""

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
with the study command. You can also search the Source Resource Document with
the srd command. You can add your own campaign files in markdown format, and
they can be loaded as well.

The initiative command will allow you to set up an order for combat, using 
creatures and player characters loaded from the SRD and your campaign files.
The next command can be used to advance the initiative count. The kill command
removes creatures from the initiative count. The heal, hit, and hp commands
can be use to manage the hit points of creatures. The attack command handles
an attack from the current creature on another creature.

The encounter command can be used to set up combats ahead of time. There are
ways you can use this for random encounters.

During combat you are shown an abbreviated stat block for the currently acting
creature. You can get the full stat block for that (or any other) creature 
using the stats command. The show command prints the initiative order again if 
you lose track of it.
"""

class Egor(cmd.Cmd):
	"""
	A helper for a D&D Dungeon master. (cmd.Cmd)

	Attributes:
	alarms: Alarms that have been set based on self.time. (list of tuple)
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
	zoo: The creatures loaded for combat. (dict of str: Creature)

	Class Attributes:
	aliases: Different names for commands. (dict of str: str)
	help_text: Additional help text. (dict of str: str)
	tag_regex: A regular expression for note tags. (Pattern)
	time_vars: Variables for game time and alarms. (dict of str: str)

	Methods:
	alarm_check: Check for any alarms that should have gone off. (None)
	combat_text: Print a summary of the current combat. (None)
	do_alarm: Set an alarm. (None)
	do_ac: Set the armor class modifier for a creature. (None)
	do_condition: Add a condition to a creature. (con)
	do_day: Advance the time by day increments. (None)
	do_encounter: Create an encounter for a later combat. (None)
	do_heal: Heal a creature. (None)
	do_hit: Do damage to a creature. (None)
	do_hp: Set a creature's HP. (None)
	do_kill: Remove a creature from the initiative order. (None)
	do_next: Show the next person in the initiative queue. (None)
	do_note: Record a note. (None)
	do_quit: Exit the Egor interface. (True)
	do_roll: Roll some dice. (None)
	do_save: Have a creature make a saving throw. (None)
	do_set: Set one of the options. (None)
	do_skill: Have a creature make a skill check. (None)
	do_srd: Search the Source Resource Document. (None)
	do_stats: Show the full stat block for a given creature. (None)
	do_store: Save the current data. (None)
	do_study: Study previously recorded notes. (None)
	do_time: Update the current game time. (None)
	do_uncondition: Remove a condition from a creature. (None)
	get_creature: Get a creature to apply a command to. (Creature)
	load_campaign: Load stored campaign data. (None)
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

	aliases = {'@': 'attack', '&': 'note', 'con': 'condition', 'init': 'initiative', 'n': 'next', 
		'q': 'quit', 'r': 'roll', 't': 'time', 'uncon': 'uncondition'}
	intro = 'Welcome, Master of Dungeons.\nI am Egor, allow me to assist you.\n'
	help_text = {'conditions': HELP_CONDITIONS, 'help': HELP_GENERAL}
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

	def combat_text(self):
		"""Print a summary of the current combat. (None)"""
		if self.init_count == 0:
			print(f'It is now Round {self.round}')
		print(self.init[self.init_count].combat_text())
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
		print(f"{creature.name}'s armor class is now {creature.ac} + {creature.ac_mod} = {total_ac}")

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

	def do_attack(self, arguments):
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
		attacker = self.init[self.init_count]
		# Make the attack
		try:
			total, text = attacker.attack(target, attack, advantage, bonus)
		except ValueError:
			# Handle attack errors.
			print(f'{attacker.name} does not have an attack named {attack!r}')
			print(f'{attacker.name} has the following attacks:')
			for letter, attack in zip(creature.Creature.letters, attacker.attacks):
				print(f'   {letter}: {attack}')
			return
		print(text)

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
		print(f'{target.name} now has the condition {condition}.')

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
			print('You must provide an encounter name.')
			return
		self.encounters[name] = []
		while True:
			# Get the monster.
			bad_guy = input('Bad guy name: ').strip()
			if not bad_guy:
				break
			#bad_guy = bad_guy.replace(' ', '-')
			if bad_guy not in self.zoo:
				print('Only creatures in the SRD or the campaign files can be used in encounters.')
				continue
			# Get the number of monsters.
			# !! needs groups, do with one in the init, no number, all in combatants.
			count = input('Number of bad guys: ')
			if count.strip():
				if not (count.isdigit() or dice.DICE_REGEX.match(count)):
					print('Invalid count, please enter that creature again.')
					continue
			else:
				count = 1
			self.encounters[name].append((bad_guy, count))
		self.changes = True

	def do_git(self, arguments):
		"""Egor doesn't understand git."""
		print('You need to quit out of Egor to commit anything, dipshit.')

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

	def do_heal(self, arguments):
		"""
		Heal a creature.

		The arguments are a creature name or initiative order number, and a number
		of points of healing for that creature.
		"""
		target_id, healing = arguments.split()
		target = self.get_creature(target_id)
		target.heal(int(healing))
		if target.hp_temp:
			print(f'{target.name} now has {target.hp} HP and {target.hp_temp} temporary HP.')
		else:
			print(f'{target.name} now has {target.hp} HP.')

	def do_hit(self, arguments):
		"""
		Do damage to a creature.

		The arguments are a creature name or initiative order number, and a number
		of points of damage to do to that creature.
		"""
		# Parse the arguments.
		target_id, damage = arguments.split()
		target = self.get_creature(target_id)
		# Apply the damage.
		target.hit(int(damage))
		if target.hp_temp:
			print(f'{target.name} now has {target.hp} HP and {target.hp_temp} temporary HP.')
		else:
			print(f'{target.name} now has {target.hp} HP.')
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
			print(f'{target.name} now has {target.hp} HP and {target.hp_temp} temporary HP.')
		else:
			print(f'{target.name} now has {target.hp} HP.')

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
		"""
		# !! refactor for size
		# Parse the arguments.
		arg_words = arguments.split()
		add = '+' in arg_words or 'add' in arg_words
		encounter = '&' in arg_words or 'encounter' in arg_words
		self.auto_attack = not add and 'auto' in arg_words
		# Check for the encounter (if it's random the DM will want to know who it is first)
		if encounter:
			enc_name = input('Encounter name: ')
			if enc_name[0] == '$':
				enc_re = re.compile(enc_name[1:])
				possible = [name for name in self.encounters if enc_re.match(name)]
				if possible:
					enc_name = random.choice(possible)
				else:
					print('There is no encounter matching that expression.')
					return
			else:
				enc_name = enc_name.strip().lower()
			print('\nThe encounter has:')
			encounter = []
			for name, roll in self.encounters[enc_name]:
				count = dice.roll(roll)
				print(f'{count}x {name}')
				encounter.append((name, str(count)))
			print('')
		# If you are not adding, set up the initiative and the PCs.
		if not add:
			# Set up the initiative tracking.
			self.init = []
			self.combatants = self.pcs.copy()
			self.init_count = 0
			self.round = 1
			# Get initiative for the PCs.
			for name, pc in self.combatants.items():
				init = input(f'Initiative for {name.capitalize()}? ')
				# Roll initiative if none given.
				if init.strip():
					pc.initiative = int(init)
				else:
					pc.init()
				self.init.append(pc)
		# Get and add an encounter if requested.
		# !! move to front so DM knows random encounters before asking for initiatives.
		if encounter:
			for name, roll in encounter:
				data = self.zoo[name]
				count = dice.roll(roll)
				for bad_guy in range(count):
					if count > 1:
						sub_name = f'{name}-{bad_guy + 1}'
					else:
						sub_name = name
					npc = data.copy(sub_name)
					npc.init()
					self.init.append(npc)
					self.combatants[npc.name.lower()] = npc
		# Otherwise get the monsters from the DM.
		else:
			while True:
				# Get the monster.
				name = input('Bad guy name: ').strip()
				if not name:
					break
				name = name.replace(' ', '-')
				# Get the number of monsters.
				count = input('Number of bad guys: ').lower()
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
					# !! need a way out of this for mistakes.
					init = int(input('Bad guy initiative bonus: '))
					data = creature.Creature(srd.HeaderNode(f'# {name}'))
					data.init_bonus = init
				# Create an roll initiative for the bad guys.
				for bad_guy in range(count):
					# Number the bad guys if there's more than one.
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
					npc = data.copy(sub_name)
					npc.init()
					self.init.append(npc)
		# Sort by the initiative rolls.
		if add:
			# Save the current point in combat, if adding to the combat.
			current = self.init[self.init_count]
			self.init.sort(key = lambda c: (c.initiative, c.bonuses['dex']), reverse = True)
			self.init_count = self.init.index(current)
		else:
			self.init.sort(key = lambda c: (c.initiative, c.bonuses['dex']), reverse = True)
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
			print(f'No creature named {arguments!r} was found.')
			return
		# Remove the creature.
		del self.init[death_index]
		if death_index < self.init_count:
			self.init_count -= 1
		# Show the current status.
		if quiet:
			print(f'{creature.name} has been removed from the initiative order.')
		else:
			self.combat_text()

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
		self.new_note(arguments)
		self.changes = True
		print('Your note has been added to the scroll, master.')

	def do_quit(self, arguments):
		"""Say goodbye to Egor."""
		if self.changes:
			choice = input('But, master! The game state has changed! Shall I save it? ')
			if choice.lower() in ('yes', 'y', 'da'):
				self.do_store('')
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
			print(f'{target.name} made the save with a {roll}.')
		else:
			print(f'{target.name} failed the save with a {roll}.')

	def do_set(self, arguments):
		"""
		Set one of the options.

		The options you can set include:
		
		* auto-kill: If set to true/1/yes, Egor automatically removes non-pc
			creatures from the initiative order when they hit 0 hp. If set to
			false/0/no, you must manually remove them with the kill command.
		* campaign: Sets the campaign folder and loads any markdown files from
			that folder that start with two digits and a period (.).
		* time-var: Changes or adds time variables (see the time command). Follow
			time-var with a time variable name and a time specification, such as
			'set time-var short-rest 5'. Setting a time variable to another time
			variable does not work.
		"""
		option, setting = arguments.split(None, 1)
		option = option.lower()
		if option == 'auto-kill':
			if setting.strip() in ('true', '1', 'yes', 't', 'y'):
				self.auto_kill = True
				print('Auto-kill is on.')
			elif setting.strip() in ('false', '0', 'no', 'f', 'n'):
				self.auto_kill = False
				print('Auto-kill is off.')
			else:
				print('Invalid setting for auto-kill.')
				return
			self.changes = True
		elif option == 'campaign':
			self.campaign_folder = setting
			self.load_campaign()
			print(f'The campaign at {self.campaign_folder} has been loaded.')
			self.changes = True
		elif option == 'time-var':
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
			choice = input('Which skill is the check for? ')
			skill = skills[int(choice)]
			print()
		# Make the skill check.
		for target in targets:
			roll, check = target.skill_check(skill, advantage, ability)
			if passive:
				passive_check = 10 + target.skills[skill] + 5 * advantage
				print(f'{target.name} rolled a {roll} for a total of {check} (passive = {passive_check}).')
			else:
				print(f'{target.name} rolled a {roll} for a total of {check}.')

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
		with open('dm.dat', 'w') as data_file:
			# Save the alarms.
			for alarm in self.alarms:
				data_file.write('alarm: {}\n'.format(alarm.data()))
			# Save the auto-kill setting.
			data.file.write('auto-kill: {}\n'.format(self.auto_kill))
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
			# Save the loaded campaign, if any.
			if self.campaign_folder:
				data_file.write('campaign: {}\n'.format(self.campaign_folder))
			# Save any encounters.
			if self.encounters:
				for name, bad_guys in self.encounters.items():
					bad_texts = [f'{name}, {count}' for name, count in bad_guys]
					enc_text = 'encounter: {} = {}\n'.format(name, '; '.join(bad_texts))
					data_file.write(enc_text)
		self.changes = False
		print('I have stored all of the incantations, master.')

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
					if isinstance(intro, srd.TextNode) and intro.lines[0][:5] in sizes:
						print(intro.parent)
						monster = creature.Creature(node)
						self.zoo[monster.name] = monster
					elif node.level < 3:
						search = [kid for kid in node.children if isinstance(kid, srd.HeaderNode)] + search

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
			print(f'{target.name} no longer has the condition {condition}.')
		else:
			print(f'{target.name} did not have the condition {condition} to remove.')

	def get_creature(self, creature, context = 'open'):
		"""
		Get a creature to apply a command to. (Creature)

		Parameters:
		creature: The identifier of the creature. (str)
		scope: How narrow/broad the search should be. (str)
		"""
		# Check the combat containers
		if creature.lower() in self.combatants:
			creature = self.combatants[creature.lower()]
		elif creature.isdigit():
			try:
				creature = self.init[int(creature) - 1]
			except ValueError:
				raise ValueError('Creature index out of range')
		# Check non-combat containers outside of combat.
		elif context == 'open' and creature.lower() in self.pcs:
			creature = self.pcs[creature.lower()]
		elif context == 'open' and creature.lower() in self.zoo:
			creature = self.zoo[creature.lower()]
		# Warn on not finding the creature.
		else:
			raise ValueError(f'No creature named {creature!r} was found.')
		# Handle ids within groups.
		if 'group-of' in creature.name:
			count = creature.name.split('-')[-1]
			name = creature.name[:creature.name.index('-group')]
			which = input(f'Which {name} (1-{count})? ')
			creature = self.get_creature(f'{name}-{which}')
		return creature

	def load_campaign(self):
		"""Load stored campaign data. (None)"""
		self.campaign = srd.SRD(self.campaign_folder)
		self.zoo.update(self.campaign.zoo)
		self.pcs = self.campaign.pcs

	def load_data(self):
		"""Load any stored state data. (None)"""
		with open('dm.dat') as data_file:
			for line in data_file:
				tag, data = line.split(':', 1)
				if tag == 'alarm':
					self.alarms.append(gtime.Alarm.from_data(data.strip()))
				if tag == 'auto-kill':
					self.auto_kill = data.strip() == 'True'
				elif tag == 'campaign':
					self.campaign_folder = data.strip()
				elif tag == 'encounter':
					name, bad_guys = data.split('=')
					name = name.strip()
					bad_texts = bad_guys.split(';')
					self.encounters[name] = []
					for text in bad_texts:
						bad_name, count = text.split(',')
						self.encounters[name].append((bad_name.strip(), count.strip()))
				elif tag == 'note':
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
		self.zoo = self.srd.zoo.copy()
		# Set the default state.
		self.alarms = []
		self.auto_kill = True
		self.campaign_folder = ''
		self.changes = False
		self.combatants = {}
		self.encounters = {}
		self.init = []
		self.notes = []
		self.time = gtime.Time(1, 1, 6, 0)
		self.time_vars = Egor.time_vars.copy()
		self.tags = collections.defaultdict(list)
		# Load any saved state.
		try:
			self.load_data()
			print('The game state has been restored, master.')
		except FileNotFoundError:
			pass
		if self.campaign_folder:
			self.load_campaign()
		# Formatting.
		print()

if __name__ == '__main__':
	egor = Egor()
	egor.cmdloop()
