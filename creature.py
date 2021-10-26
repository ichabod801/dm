"""
creature.py

Creatures for combat and information.

Constants:
EMPHASIS_REGEX: A regex matching emphasized text in markdown. (Pattern)

Classes:
Attack: An attack used by a creature. (object)
Creature: A creature for combat or information. (object)
CreatureGroup: A grouping of similar creatures. (object)
DummyNode: A fake header node for creating blank creatures. (namedtuple)
ParsingError: A custom error from parsing problems. (Exception)
"""

import collections
import re

from . import dice

EMPHASIS_REGEX = re.compile(r'(?P<em>\*{1,3}|_{1,3})([^\*_]+?)(?P=em)')

class Attack(object):
	"""
	An attack used by a creature. (object)

	The damage attribute is a list of tuples containing the text defining the
	damage roll, and the type of damage done.

	Attributes:
	additional: A description of any additional effects of the attack. (str)
	bonus: The attack bonus for the attack. (int)
	damage: The damage done by the attack. (list of (str, str))
	melee: A flag for the attack being a melee attack. (bool)
	name: The name of the attack. (str)
	or_damage: The damage is alternatives, not combined. (bool)
	range: The range and/or reach for the attack. (str)
	ranged: A flag for the attack being a ranged attack. (bool)
	text: The text describing the attack. (str)
	spell: A flag for the attack being a spell attack. (bool)

	Methods:
	add_text: Add further explanatory text to the attack. (None)
	attack: Make the attack. (tuple of int, str)
	base_text: Base text for string representations. (str)
	full_text: Full text representation. (str)

	Overridden Methods:
	__init__
	__repr__
	__str__
	"""

	def __init__(self, title, text):
		"""
		A temporary initializer for testing. (None)

		Parameters:
		title: The name of the attack. (str)
		text: The text explaining the attack. (str)
		"""
		# Set the text attributes.
		self.name = title
		self.text = text
		# Parse the attack type attributes.
		self.melee = 'Melee' in self.text
		self.ranged = 'Ranged' in self.text
		self.spell = 'Spell' in self.text
		self.or_damage = False
		# Get the attack bonus.
		attack = self.text.index('Attack:*') + 8
		bonus_word = self.text[attack:].split()[0]
		self.bonus = int(bonus_word.strip('+'))
		# Get the range or reach.
		comma = self.text.index(',', attack) + 1
		hit = self.text.index('*Hit:*')
		self.range = self.text[comma:hit].strip(' .')
		# Parse the hit text.
		hit += 6
		period = self.text.index('.', hit)
		hit_text = self.text[hit:period]
		self.damage = []
		roll = ''
		roll_done = False
		for word in hit_text.split():
			# Check for start of damage roll.
			if word.startswith('('):
				if word.endswith(')'):
					roll = word[1:-1]
					roll_done = True
				else:
					roll = word[1:]
			# Pick up the word after the damage roll as the damage type.
			elif roll_done:
				self.damage.append((roll, word))
				roll = ''
				roll_done = False
			# Check for the end of a damage roll with a space in it.
			elif roll:
				if word.endswith(')'):
					roll += word[:-1]
					roll_done = True
				else:
					roll += word
			# Check for different damage rolls as opposed to multiple damage rolls.
			elif word == 'or':
				self.or_damage = True
		# Get any additional effects.
		if not self.damage:
			# Roll back one sentence.
			period = hit
		self.additional = self.text[(period + 1):].strip()

	def __repr__(self):
		"""Debugging text representation. (str)"""
		damage_bits = [f'{roll} {damage_type}' for roll, damage_type in self.damage]
		if self.or_damage:
			damage_text = ' or '.join(damage_bits)
		else:
			damage_text = ', '.join(damage_bits)
		more_text = '...' if self.additional else ''
		space = ' ' if self.damage and self.additional else ''
		return f'<Attack {self.name} {self.bonus} {damage_text}{space}{more_text}>'

	def __str__(self):
		"""Human readable text representation. (str)"""
		base_text = self.base_text()
		more_text = ' and more' if self.additional else ''
		return f'{base_text}{more_text}'

	def add_text(self, text):
		"""
		Add further explanatory text to the attack. (None)

		Parameters:
		text: The extra explanatory text. (str)
		"""
		self.additional = '{} {}'.format(self.additional, text)

	def attack(self, target, advantage = 0, temp_bonus = 0):
		"""
		Make the attack. (tuple of int, str)

		The return value is the total damage and text describing the damage.

		Parameters:
		target: The target of the attack. (Creature)
		advantage: The advantage or disadvantage for the attack. (int)
		temp_bonus: A temporary bonus to the to hit roll. (int)
		"""
		# Make the attack roll.
		hit_roll = dice.d20(advantage)
		total_bonus = self.bonus + temp_bonus
		# Determine the target AC.
		if target is None:
			target_ac = 1
		else:
			target_ac = target.ac + target.ac_mod
		# Handle fumbles.
		if hit_roll == 1:
			total = 0
			text = 'Fumble'
		# Handle hits.
		elif hit_roll == 20 or hit_roll + total_bonus >= target_ac:
			# Get the damage.
			text_bits = []
			total = 0
			for roll, damage in self.damage:
				sub_total = dice.roll(roll)
				if hit_roll == 20:
					sub_total += dice.roll(roll)
				s = '' if sub_total == 1 else 's'
				text_bits.append(f'{sub_total} point{s} of {damage} damage')
				if self.or_damage:
					total = sub_total
				else:
					total += sub_total
			if target is not None:
				target.hit(total)
				print(f'{target.name.capitalize()} has {target.hp} hit points left.')
			# Create the text description.
			if target is None:
				hit_type = 'Critical hit' if hit_roll == 20 else f'Hits AC {hit_roll + total_bonus}'
			else:
				hit_type = 'Critical hit' if hit_roll == 20 else f'Hit ({hit_roll} + {total_bonus})'
			if len(text_bits) == 1:
				text = f'{hit_type} for {text_bits[0]}'
			else:
				s = '' if total == 1 else 's'
				if self.or_damage:
					text = f"{hit_type} for {total} point{s}; {' or '.join(text_bits)}"
				else:
					text = f"{hit_type} for {total} point{s}; {', '.join(text_bits)}"
			if self.additional:
				text += f'; {self.additional}'
		# Handle normal misses.
		else:
			total = 0
			text = f'Miss ({hit_roll} + {total_bonus})'
		return total, text

	def base_text(self):
		"""Base text for string representations. (str)"""
		plus = '+' if self.bonus > -1 else ''
		damage_bits = [f'{roll} {damage_type}' for roll, damage_type in self.damage]
		if self.or_damage:
			damage_text = ' or '.join(damage_bits)
		else:
			damage_text = ', '.join(damage_bits)
		return f'{self.name}, {plus}{self.bonus} to hit, {self.range}, {damage_text}'

	def full_text(self):
		"""Full text representation. (str)"""
		base_text = self.base_text()
		if self.additional:
			return f'{base_text}. {self.additional}'
		else:
			return base_text

class Creature(object):
	"""
	A creature for combat or information. (object)

	The full definitions for most of the creature's attributes are in the Monster
	Manual.

	Attributes:
	abilities: The creature's ability scores. (dict of str: int)
	ac: The creature's armor class. (str)
	ac_mod: Any temporary modifier to armor class. (str)
	ac_text: The text describing the reason for the creature's armor class. (str)
	actions: Actions the creature can take. (dict of str: str)
	alignment: The creature's alignment. (str)
	attacks: The creature's attack actions. (dict of str: Attack)
	bonuses: The creature's ability bonuses. (dict of str: int)
	conditions: Any conditions affecting the creature, with timers. (list of lists)
		sub-lists are condition, rounds, creature's round to end on, start or end.
	cr: The creature's challenge rating. (int)
	description: The creature's descriptive text. (str)
	features: Non-action features of the creature. (dict of str: str)
	hp: The creature's current hit points. (int)
	hp_max: The creature's maximum hit points. (int)
	hp_roll: The roll specification to determine the creature's hit points. (str)
	hp_temp: The creature's temporary hit points. (int)
	init_bonus: The creature's initiative bonus. (int)
	initiative: The creature's current combat priority. (int)
	language: The languages the creature can speak. (str)
	legendary: Legendary actions the creature can take. (dict of str: str)
	name: The creature's name. (str)
	name_regex: A regular expression for the creature's name emphasized. (Pattern)
	other_speeds: The creature's non-walking speeds, if any. (str)
	pc: A flag for the creature being a player character. (bool)
	reactions: The text for the creature's reactions. (dict of str: str)
	saves: The creature's saving throw bonuses. (dict of str: int)
	skills: The creature's skill bonuses. (dict of str: int)
	size: The creature's size category. (str)
	speed: How many feet the creature can move per round. (int)
	sub_type: The creature's sub-type. (str)
	type: The creature's type. (str)
	xp: The creature's experience point value. (int)

	Class Attributes:
	letters: Letters for identifying attacks. (str)
	sizes: The valid starts of the size/type/alignment line. (tuple of str)
	skill_abilities: The ability bonus for each skill. (tuple of str: str)
	two_start: Parser names for lines starting with '**'. (dict of str: str)

	Methods:
	_parse_abilities: Parse the creature's ability scores and bonuses. (None)
	_parse_ac: Parse the creature's armor class. (None)
	_parse_action: Parse one of the creature's actions. (None)
	_parse_challenge: Parse the creature's challenge rating. (None)
	_parse_feature: Parse one of the creature's non-action features. (None)
	_parse_header: Parse special headers in the creature description. (None)
	_parse_hp: Parse the creature's hit points. (None)
	_parse_languages: Parse the creature's languages. (None)
	_parse_legendary: Parse one of the creature's legendary actions. (None)
	_parse_lines: Parse the lines of a text node. (None)
	_parse_reaction: Parse one of the creature's actions. (None)
	_parse_saves: Parse the creature's saving throw bonuses. (None)
	_parse_senses: Parse the creature's languages. (None)
	_parse_size: Parse the creature's size, type, sub-type, and alignment. (None)
	_parse_skills: Parse the creature's skill bonuses. (None)
	_parse_speed: Parse the creature's movement speed. (None)
	_set_defaults: Set the default attributes for a creature. (None)
	auto_attack: Do all attacks without a target. (str)
	attack: Attack something. (tuple of int, text)
	combat_text: Text representation for their turn in combat. (str)
	copy: Create an independent version of the creature. (Creature)
	heal: Heal damage to the creature. (int)
	hit: Handle the creature taking damage. (int)
	init: Roll initiative for the creature. (int)
	save: Make a saving throw. (tuple of int, bool)
	skill_check: Make a skill check. (tuple of int)
	stat_block: Full text representation. (str)
	update_conditions: Check conditions for expired ones. (None)

	Overridden Methods:
	__init__
	__repr__
	__str__
	"""

	letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	sizes = ('*Tiny', '*Smal', '*Medi', '*Larg', '*Huge', '*Garg')
	skill_abilities = {'acrobatics': 'dex', 'arcana': 'int', 'animal-handling': 'wis', 'athletics': 'str',
		'deception': 'cha', 'history': 'int', 'insight': 'wis', 'intimidation': 'cha', 
		'investigation': 'int', 'medicine': 'wis', 'nature': 'int', 'perception': 'wis', 
		'performance': 'cha', 'persuasion': 'cha', 'religion': 'int', 'sleight-of-hand': 'dex', 
		'stealth': 'dex', 'suvival': 'wis'}
	two_stars = {'Armor Class': '_parse_ac', 'Challenge': '_parse_challenge', 'Hit Points': '_parse_hp', 
		'Languages': '_parse_languages', 'Saving Throws': '_parse_saves', 'Senses': '_parse_senses', 
		'Skills': '_parse_skills', 'Speed': '_parse_speed'}

	def __init__(self, node):
		"""
		Read the creature's statistics. (None)

		Parameters:
		node: The creature's header node in a SRD style document. (HeaderNode)
		"""
		# Set the creature's name.
		self.name = node.name.strip()
		self.name_regex = re.compile(r'\*\*{}e?s?\*\*'.format(self.name), re.IGNORECASE)
		# Set the creature's default attributes.
		self._set_defaults()
		# Loop through the node content.
		for node in node.children:
			if hasattr(node, 'lines'):  # if it has lines then it is a TextNode (avoids circular import)
				self._parse_lines(node)
			else:
				try:
					self._parse_header(node)
				except:
					raise ParsingError(f'Error parsing {self.name} in header {node.name!r}.')

	def __repr__(self):
		"""Debugging text representation. (str)"""
		return f'<Creature {self.name}, {self.size} {self.type}>'

	def __str__(self):
		"""Human readable text representation. (str)"""
		text = f'{self.name}; AC {self.ac + self.ac_mod}; HP {self.hp}/{self.hp_max}'
		if self.conditions:
			text = '{}; {}'.format(text, ', '.join([con[0] for con in self.conditions]))
		return text

	def _parse_abilities(self, line):
		"""
		Parse the creature's ability scores and related bonuses. (None)

		Parameters:
		line: The line of text with the creature's ability scores. (str)
		"""
		# Set up the attribute dicts.
		self.abilities, self.bonuses, self.saves, self.skills = {}, {}, {}, {}
		# Get the abilities, with bonuses and default saves.
		cells = line.split('|')
		for ability, text in zip(('str', 'dex', 'con', 'int', 'wis', 'cha'), cells[1:]):
			score = int(text.split()[0])
			self.abilities[ability] = score
			self.bonuses[ability] = score // 2 - 5
			self.saves[ability] = score // 2 - 5
		# Get the default skill bonuses.
		for skill, ability in self.skill_abilities.items():
			self.skills[skill] = self.bonuses[ability]
		# Set the initiative bonus.
		self.init_bonus = self.bonuses['dex']

	def _parse_ac(self, title, text):
		"""
		Parse the creature's armor class. (None)

		Parameters:
		title: The title of the paragraph. (str)
		text: The text of the paragraph with the creature's AC. (str)
		"""
		parts = text.split(None, 1)
		self.ac = int(parts[0])
		self.ac_text = parts[1].strip(' ()') if len(parts) > 1 else ''

	def _parse_action(self, name, text):
		"""
		Parse one of the creature's actions. (None)

		Parameters:
		name: The emphasized text at the start of the line. (str)
		text: The rest of the text on the line. (str)
		"""
		if 'Attack:*' in text:
			self.attacks[name] = Attack(name, text[1:].strip())
			return self.attacks, name
		else:
			self.actions[name] = text[1:].strip()
			return self.actions, name

	def _parse_challenge(self, title, text):
		"""
		Parse the creature's challenge rating. (None)

		Parameters:
		title: The title of the paragraph. (str)
		text: The text of the paragraph with the creature's CR and XP. (str)
		"""
		parts = text.split('(')
		if '/' in parts[0]:
			numerator, denominator = parts[0].split('/')
			self.cr = int(numerator) / int(denominator)
		else:
			self.cr = int(parts[0])
		self.xp = int(parts[1][:parts[1].index('X')].replace(',', ''))

	def _parse_feature(self, title, text):
		"""
		Parse one of the creature's non-action features. (None)

		Parameters:
		title: The title of the paragraph. (str)
		text: The text of the paragraph with a non-action feature. (str)
		"""
		self.features[title] = text[1:].strip() # [1:] gets rid of punctuation after title.
		return self.features, title

	def _parse_header(self, node):
		"""Parse special headers in the creature description. (None)"""
		last_key = ''
		last_dict = None
		# Search through the actions section.
		if node.name.strip() == 'Actions':
			for child in node.children:
				for line in child.lines:
					match = EMPHASIS_REGEX.match(line)
					# Handle named actions.
					if match:
						blank, name, text = line.split(match.group(1), 2)
						last_dict, last_key = self._parse_action(name, text)
					# Add unnamed actions to the last action.
					elif line.strip():
						if self.name_regex.search(line):
							self.description = line
							last_dict = 'description'
						elif last_dict == 'description':
							self.description = f'{self.description}\n\n{line}'
						elif last_dict == self.actions:
							last_dict[last_key] = '{}\n\n{}'.format(last_dict[last_key], line)
						else:
							last_dict[last_key].add_text(line)
		# Search through the actions section.
		if node.name == 'Reactions':
			for child in node.children:
				for line in child.lines:
					match = EMPHASIS_REGEX.match(line)
					# Handle named actions.
					if match:
						blank, name, text = line.split(match.group(1), 2)
						last_dict, last_key = self._parse_reaction(name, text)
					# Add unnamed actions to the last action.
					elif line.strip():
						if last_dict == self.reactions:
							last_dict[last_key] = '{}\n\n{}'.format(last_dict[last_key], line)
						else:
							last_dict[last_key].add_text(line)
		# Search through the legendary actions section, if any.
		elif node.name == 'Legendary Actions':
			last_key = ''
			for child in node.children:
				for line in child.lines:
					match = EMPHASIS_REGEX.match(line)
					# Handle named actions.
					if match:
						blank, name, text = line.split(match.group(1), 2)
						last_key = self._parse_legendary(name, text)
					# Check for loose paragraphs.
					elif line.strip():
						# Add to previous legendary actions.
						if last_key:
							new_text = '{}\n\n{}'.format(self.legendary[last_key], line)
							self.legendary[last_key] = new_text
						# Assume the first one describes legendary actions in general.
						else:
							self.legendary['Legendary Actions'] = line

	def _parse_hp(self, title, text):
		"""
		Parse the creature's hit points. (None)

		Parameters:
		title: The title of the paragraph. (str)
		text: The text of the paragraph with the creature's HP. (str)
		"""
		# Parse the average hit points and hit point roll.
		parts = text.split('(')
		self.hp = int(parts[0])
		self.hp_roll = parts[1].strip(') ')
		# Set the secondary hit point attributes.
		self.hp_max = self.hp
		self.hp_temp = 0

	def _parse_languages(self, title, text):
		"""
		Parse the creature's languages. (None)

		Parameters:
		title: The title of the paragraph. (str)
		text: The text of the paragraph with the creature's languages. (str)
		"""
		self.languages = text.strip()

	def _parse_legendary(self, name, text):
		"""
		Parse one of the creature's legendary actions. (str)

		Parameters:
		name: The emphasized text at the start of the line. (str)
		text: The rest of the text on the line. (str)
		"""
		self.legendary[name] = text[1:].strip()
		return name

	def _parse_lines(self, node):
		"""Parse the lines of a text node. (None)"""
		abilities = False
		for line in node.lines:
			try:
				# Check for abilities.
				if abilities:
					if line[1] != '-':
						self._parse_abilities(line)
						abilities = False
				# Check for the starting size line.
				elif line[:5] in self.sizes:
					self._parse_size(line)
				# Check for starting to check for abilities.
				elif line.startswith('| STR'):
					abilities = True
				else:
					# Check for a line starting with emphasized text.
					match = EMPHASIS_REGEX.match(line)
					if match:
						blank, title, text = line.split(match.group(1))
						last = getattr(self, self.two_stars.get(title, '_parse_feature'))(title, text)
						if last is not None:
							last_dict, last_key = last
					# Append loose paragraphs to the last feature found.
					elif line.strip():
						last_dict[last_key] = '{}\n\n{}'.format(last_dict[last_key], line)
			except:
				words = ' '.join(line.split()[:3])
				raise ParsingError(f'Error parsing {self.name} on line starting with {words!r}.')

	def _parse_reaction(self, name, text):
		"""
		Parse one of the creature's actions. (None)

		Parameters:
		name: The emphasized text at the start of the line. (str)
		text: The rest of the text on the line. (str)
		"""
		self.reactions[name] = text[1:].strip()
		return self.reactions, name

	def _parse_saves(self, title, text):
		"""
		Parse the creature's saving throw bonuses. (None)

		Parameters:
		title: The title of the paragraph. (str)
		text: The text of the paragraph with the creature's saves. (str)
		"""
		for save_text in text.split(','):
			ability, bonus = save_text.split()
			self.saves[ability.strip().lower()] = int(bonus.strip('+'))

	def _parse_senses(self, title, text):
		"""
		Parse the creature's languages. (None)

		Parameters:
		title: The title of the paragraph. (str)
		text: The text of the paragraph with the creature's senses. (str)
		"""
		self.senses = text.strip()

	def _parse_size(self, line):
		"""
		Parse the creature's size, type, sub-type, and alignment. (None)

		Parameters:
		line: The line of text with the creature's size. (str)
		"""
		words = line.split()
		# Get the creature's size.
		self.size = words[0].strip('*')
		# Get the creature's type and optional sub-type.
		self.type = words[1].strip(',')
		if '(' in line:
			start = line.index('(') + 1
			end = line.index(')')
			self.sub_type = line[start:end]
		else:
			self.sub_type = ''
		# Get the creature's alignment.
		self.alignment = line[line.index(',') + 1:].strip(' *')

	def _parse_skills(self, title, text):
		"""
		Parse the creature's skill bonuses. (None)

		Parameters:
		title: The title of the paragraph. (str)
		text: The text of the paragraph with the creature's skills. (str)
		"""
		for skill_text in text.split(','):
			skill, bonus = skill_text.rsplit(None, 1)
			try:
				self.skills[skill.strip().lower().replace(' ', '-')] = int(bonus.strip('+'))
			except ValueError:
				main, qualifier = skill_text.split('(')
				skill, bonus = main.rsplit(None, 1)
				self.skills[skill.strip().lower().replace(' ', '-')] = int(bonus.strip('+'))
				self._parse_feature(skill, f" {qualifier.strip(')')}")

	def _parse_speed(self, title, text):
		"""
		Parse the creature's movement speed. (None)

		Parameters:
		title: The title of the paragraph. (str)
		text: The text of the paragraph with the creature's speed. (str)
		"""
		# Handle creatures with other speeds.
		if ',' in text:
			base, other = text.split(',', 1)
			self.speed = int(base.split()[0])
			self.other_speeds = other.strip()
		# Handle land-speed only creatures.
		else:
			self.speed = int(text.split()[0])
			self.other_speeds = ''

	def _set_defaults(self):
		"""Set the default attributes for a creature."""
		self.ac = 10
		self.abilities = {'str': 10, 'dex': 10, 'con': 10, 'int': 10, 'wis': 10, 'cha': 10}
		self.bonuses = {'str': 0, 'dex': 0, 'con': 0, 'int': 0, 'wis': 0, 'cha': 0}
		self.saves = self.bonuses.copy()
		self.actions, self.attacks, self.features = {}, {}, {}
		self.conditions = []
		self.legendary, self.reactions = {}, {}
		self.ac_mod, self.cr, self.hp_temp, self.hp_max, self.init_bonus = 0, 0, 0, 0, 0
		self.initiative, self.xp = 0, 0
		self.description = ''
		self.hp_roll = '20d12'
		self.hp, self.hp_max = 140, 140
		self.pc = False
		self.size = 'Medium'
		self.skills = {skill: 0 for skill in self.skill_abilities}
		self.speed = 30
		self.other_speeds = ''
		self.type = 'unknown'

	def auto_attack(self):
		"""Do all attacks without a target. (str)"""
		results = []
		for attack in self.attacks.values():
			damage, text = attack.attack(None)
			results.append(f'**{attack.name}**: {text}')
		return '\n'.join(results)

	def attack(self, target, name, advantage = 0, temp_bonus = 0):
		"""
		Attack something. (tuple of int, str)

		Parameters:
		target: The creature to attack. (Creature)
		name: The name of the attack to use. (str)
		advantage: The advantage/disadvantage for the attack. (int)
		temp_bonus: A temporary bonus to the to hit roll. (int)
		"""
		# Get the attack by letter.
		if len(name) == 1:
			name = list(self.attacks.keys())[self.letters.index(name.upper())]
			attack = self.attacks[name]
		# Get the attack by name.
		elif name:
			name = name.lower().replace('-', ' ')
			for attack in self.attacks.values():
				if attack.name.lower() == name.lower():
					break
			else: 
				raise ValueError('No such attack.')
		# Get the default attack.
		else:
			name = list(self.attacks.keys())[0]
			attack = self.attacks[name]
		# Make the attack.
		return attack.attack(target, advantage, temp_bonus)

	def combat_text(self):
		"""Text representation for their turn in combat. (str)"""
		# Set up header.
		lines = ['-------------------', self.name]
		if self.conditions:
			lines.append(', '.join([con[0] for con in self.conditions]))
		lines.append('-------------------')
		#lines.extend(['', '-------------------', ''])
		# Set up speed/hp section.
		speed_text = f'Speed: {self.speed} ft.'
		if self.other_speeds:
			speed_text = f'{speed_text}; {self.other_speeds}'
		lines.append(speed_text)
		lines.append(f'AC: {self.ac}')
		if self.hp_temp:
			lines.append(f'HP: {self.hp}+{self.hp_temp}/{self.hp_max}')
		else:
			lines.append(f'HP: {self.hp}/{self.hp_max}')
		lines.append('-------------------')
		#lines.extend(['', '-------------------', ''])
		# Set up features:
		if self.features:
			lines.append('Features: {}'.format(', '.join(title for title in self.features)))
		# Set up actions:
		if self.actions:
			lines.append('Actions: {}'.format(', '.join(title for title in self.actions)))
		# Set up attacks:
		lines.append('Attacks:')
		for letter, attack in zip(self.letters, self.attacks.values()):
			lines.append(f'   {letter}: {attack}')
		# Combine the lines.
		return '\n'.join(lines)

	def copy(self, name = '', average_hp = False):
		"""
		Create an independent copy of the creature. (Creature)

		Parameters:
		name: The name for the new creature. (str)
		average_hp: A flag for using the average HP. (str)
		"""
		if not name:
			name = self.name
		clone = Creature(DummyNode(name, []))
		clone.__dict__ = self.__dict__.copy()
		clone.name = name
		clone.conditions = self.conditions[:]
		if not average_hp:
			clone.hp = dice.roll(clone.hp_roll)
			clone.hp_max = clone.hp
		return clone

	def heal(self, hp):
		"""
		Heal damage to the creature. (int)

		Parameters:
		hp: The amount of damage to heal. (int)
		"""
		if hp < 0:
			return self.hit(abs(hp))
		self.hp = min(self.hp + hp, self.hp_max)
		return self.hp

	def hit(self, hp):
		"""
		Handle the creature taking damage. (int)

		Parameters:
		hp: The amount of damage to take. (int)
		"""
		if hp < 0:
			return self.heal(abs(hp))
		for condition in self.conditions:
			if condition[0].lower().startswith('conc'):
				dc = max(10, hp // 2)
				print(f'{self.name} needs to make a concentration check (con save) of DC {dc}.')
		if self.hp_temp:
			self.hp_temp -= hp
			if self.hp_temp < 0:
				self.hp = max(self.hp + self.hp_temp, 0)
				self.hp_temp = 0
		else:
			self.hp = max(self.hp - int(hp), 0)
		return self.hp

	def init(self):
		"""Roll initiative for the creature. (int)"""
		self.initiative = dice.d20() + self.init_bonus
		return self.initiative

	def save(self, ability, dc, advantage = 0):
		"""
		Make a saving throw. (tuple of int, bool)

		Parameters:
		ability: The ability to use for the save. (str)
		dc: The difficulty class for the save. (int)
		advantage: The advantage/disadvantage for the roll. (int)
		"""
		bonus = self.saves[ability]
		roll = dice.d20(advantage) + bonus
		return roll, roll >= dc

	def skill_check(self, skill, advantage = 0, ability = ''):
		"""
		Make a skill check. (tuple of int)

		If an ability is not given, the default ability for the skill is used.

		Parameters:
		skill: The skill to check. (str)
		advantage: Whether the creature has advantage on the check. (int)
		ability: The ability to use for the check. (str)
		"""
		bonus = self.skills[skill]
		if ability:
			bonus -= self.bonuses[self.skill_abilities[skill]]
			bonus += self.bonuses[ability]
		roll = dice.d20(advantage)
		return roll, roll + bonus

	def stat_block(self):
		"""Full text representation. (str)"""
		lines = [f'## {self.name}', '']
		# Type, armor class, and speed section.
		if self.sub_type:
			lines.append(f'*{self.size} {self.type} ({self.sub_type}), {self.alignment}*')
		else:
			lines.append(f'*{self.size} {self.type}, {self.alignment}*')
		if self.ac_text:
			lines.append(f'**Armor Class** {self.ac} ({self.ac_text})')
		else:
			lines.append(f'**Armor Class** {self.ac}')
		if self.hp_temp:
			lines.append(f'**Hit Points** {self.hp}+{self.hp_temp}/{self.hp_max} ({self.hp_roll})')
		else:
			lines.append(f'**Hit Points** {self.hp}/{self.hp_max} ({self.hp_roll})')
		if self.other_speeds:
			lines.append(f'**Speed** {self.speed} ft., {self.other_speeds}')
		else:
			lines.append(f'**Speed** {self.speed} ft.')
		# Abilities section
		score_bits = []
		title_bits = []
		line_bits = []
		for ability, score in self.abilities.items():
			bonus = score // 2 - 5
			plus = '+' if bonus >= 0 else ''
			score_bits.append(f'{score} ({plus}{bonus})')
			title_format = f'{{:<{len(score_bits[-1])}}}'
			title_bits.append(title_format.format(ability.upper()))
			line_bits.append('-' * len(score_bits[-1]))
		lines.append('')
		lines.append('| {} |'.format(' | '.join(title_bits)))
		lines.append('|-{}-|'.format('-|-'.join(line_bits)))
		lines.append('| {} |'.format(' | '.join(score_bits)))
		lines.append('')
		# Features Section.
		prof_saves = {attr: bonus for attr, bonus in self.saves.items() if bonus != self.bonuses[attr]}
		if prof_saves:
			save_bits = [f'{attr.capitalize()} {bonus:+}' for attr, bonus in prof_saves.items()]
			lines.append('**Saves** {}'.format(', '.join(save_bits)))
		lines.append(f'**Senses** {self.senses}')
		lines.append(f'**Languages** {self.languages}')
		if self.cr >= 1:
			lines.append(f'**Challenge** {self.cr} ({self.xp} XP)')
		elif self.cr:
			denom = int(round(1 / self.cr, 0))
			lines.append(f'**Challenge** 1/{denom} ({self.xp} XP)')
		for name, text in self.features.items():
			text = text.replace('\n\n', '\n    ')
			lines.append(f'**{name}**. {text}')
		# Actions section
		if self.actions:
			lines.append('\n### Actions\n')
			for name, text in self.actions.items():
				text = text.replace('\n\n', '\n    ')
				lines.append(f'***{name}***. {text}')
			lines.append('')
		# Reactions section
		if self.reactions:
			lines.append('\n### Reactions\n')
			for name, text in self.reactions.items():
				text = text.replace('\n\n', '\n    ')
				lines.append(f'***{name}***. {text}')
			lines.append('')
		# Legendary ctions section
		if self.legendary:
			lines.append('\n### Legendary Actions\n')
			for name, text in self.legendary.items():
				text = text.replace('\n\n', '\n    ')
				lines.append(f'***{name}***. {text}')
			lines.append('')
		# Attacks section
		lines.append('Attacks:')
		for letter, attack in zip(self.letters, self.attacks.values()):
			lines.append(f'   {letter}: {attack.full_text()}')
		return '\n'.join(lines)

	def update_conditions(self, combatant, end_point):
		"""
		Update condition timers, and remove finished conditions. (None)

		Parameters:
		combatant: The name of the current combatant. (str)
		end_point: 's' for the start of the round, 'e' for the end. (str)
		"""
		drop = set()
		for con_index, condition in enumerate(self.conditions):
			if [combatant, end_point] == condition[2:]:
				condition[1] -= 1
				if not condition[1]:
					drop.add(con_index)
		if drop:
			new_conditions = []
			for con_index, condition in enumerate(self.conditions):
				if con_index not in drop:
					new_conditions.append(condition)
			self.conditions = new_conditions

class CreatureGroup(object):
	"""
	A grouping of similar creatures. (object)

	Attributes:
	creature_name: The name of the individual creatures. (str)
	creatures: The creatures in the group. (list of Creature)
	name: The name of the group of creatures. (str)

	Methods:
	_ac_text: Text representation of individual ACs, as needed. (str)
	_condition_text: Text representation of inidividual condtions. (str)
	_hp_text: Text representation of the individual hit points. (str)
	attack: Attack something using a proxy. (tuple of int, str)
	auto_attack: Do all attacks for all creatures without a target. (str)
	combat_text: Text representation for the group's turn in combat. (str)
	init: Roll initiative for the group. (int)
	update_conditions: Update condition tracking. (None)

	Overridden Methods:
	__init__
	__repr__
	__str__
	"""

	def __init__(self, creature_name, creatures):
		"""
		Set up the group of creatures. (None)

		Parameters:
		creature_name: The name of the individual creatures. (str)
		creatures: The creatures in the group. (list of Creature)
		"""
		# Set the given attributes.
		self.creature_name = creature_name
		self.creatures = creatures
		# Set the derived attributes
		self.abilities = self.creatures[0].abilities
		self.init_bonus = self.creatures[0].init_bonus
		self.name = f'{self.creature_name}-group-of-{len(self.creatures)}'
		# Set the default attributes.
		self.initiative = 0

	def __repr__(self):
		"""Debugging text representation. (str)"""
		return f'<CreatureGroup {self.name}, group of {len(self.creatures)}>'

	def __str__(self):
		"""Human readable text representation. (str)"""
		text = f'{self.name}; AC {self._ac_text()}; HP {self._hp_text()}'
		con_text = self._condition_text()
		if con_text:
			text = f'{text}; {con_text}'
		return text

	def _ac_text(self):
		"""Text representation of individual ACs, as needed. (str)"""
		acs = [creature.ac + creature.ac_mod for creature in self.creatures]
		if len(set(acs)) > 1:
			text = '/'.join([str(ac) for ac in acs])
		else:
			text = str(acs[0])
		return text

	def _condition_text(self):
		"""Text representation of inidividual condtions. (str)"""
		con_text = []
		for creature_index, creature in enumerate(self.creatures, start = 1):
			if creature.conditions:
				con_comma = ', '.join([con[0] for con in creature.conditions])
				con_text.append(f'{creature_index}: {con_comma}')
		return '; '.join(con_text)

	def _hp_text(self):
		"""Text representation of the individual hit points. (str)"""
		hp_text = []
		for creature in self.creatures:
			if creature.hp_temp:
				hp_text.append(f'{creature.hp}+{creature.hp_temp}/{creature.hp_max}')
			else:
				hp_text.append(f'{creature.hp}/{creature.hp_max}')
		return ', '.join(hp_text)

	def attack(self, target, name, advantage = 0, temp_bonus = 0):
		"""
		Attack something using a proxy. (tuple of int, str)

		Parameters:
		target: The creature to attack. (Creature)
		name: The name of the attack to use. (str)
		advantage: The advantage/disadvantage for the attack. (int)
		temp_bonus: A temporary bonus to the to hit roll. (int)
		"""
		return self.creatures[0].attack(target, name, advantage, temp_bonus)

	def auto_attack(self):
		"""Do all attacks for all creatures without a target. (str)"""
		lines = []
		for creature in self.creatures:
			if creature.hp > 0:
				lines.append(creature.name)
				lines.append(creature.auto_attack())
		return '\n\n'.join(lines)

	def combat_text(self):
		"""Text representation for the group's turn in combat. (str)"""
		# Set up header.
		lines = ['-------------------', self.name]
		con_text = self._condition_text()
		if con_text:
			lines.append(con_text)
		lines.append('-------------------')
		# Get a sample creature
		sample = self.creatures[0]
		# Set up speed/hp section.
		speed_text = f'Speed: {sample.speed} ft.'
		if sample.other_speeds:
			speed_text = f'{speed_text}; {sample.other_speeds}'
		lines.append(speed_text)
		lines.append(f'AC: {self._ac_text()}')
		lines.append(f'HP: {self._hp_text()}')
		lines.append('-------------------')
		# Set up features:
		if sample.features:
			lines.append('Features: {}'.format(', '.join(title for title in sample.features)))
		# Set up actions:
		if sample.actions:
			lines.append('Actions: {}'.format(', '.join(title for title in sample.actions)))
		# Set up attacks:
		lines.append('Attacks:')
		for letter, attack in zip(sample.letters, sample.attacks.values()):
			lines.append(f'   {letter}: {attack}')
		# Combine the lines.
		return '\n'.join(lines)

	def init(self):
		"""Roll initiative for the group. (int)"""
		self.initiative = dice.d20() + self.init_bonus
		return self.initiative

	def update_conditions(self, combatant, end_point):
		"""
		Update condition timers, and remove finished conditions. (None)

		Parameters:
		combatant: The name of the current combatant. (str)
		end_point: 's' for the start of the round, 'e' for the end. (str)
		"""
		for creature in self.creatures:
			creature.update_conditions(combatant, end_point)

# A fake header node for creating blank creatures.
DummyNode = collections.namedtuple('DummyNode', ('name', 'children'))

class ParsingError(Exception):
	"""A custom error from parsing problems. (Exception)"""
	pass
