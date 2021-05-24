"""
creature.py

Creatures for combat and information.

Classes:
Attack: An attack used by a creature. (object)
Creature: A creature for combat or information. (object)
DummyNode: A fake header node for creating blank creatures. (namedtuple)
"""

import collections
import re

import dice

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
	ranged: A flag for the attack being a ranged attack. (bool)
	text: The text describing the attack. (str)
	spell: A flag for the attack being a spell attack. (bool)

	Methods:
	add_text: Add further explanatory text to the attack. (None)
	attack: Make the attack. (tuple of int, str)

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
		# Parse the hit text.
		hit = self.text.index('*Hit:* ') + 6
		period = self.text.index('.', hit)
		hit_text = self.text[hit:period]
		self.damage = []
		roll = ''
		for word in hit_text.split():
			if word.startswith('(') and word.endswith(')'):
				roll = word[1:-1]
			elif roll:
				self.damage.append((roll, word))
				roll = ''
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
		"""Debugging text representation. (str)"""
		plus = '+' if self.bonus > -1 else ''
		damage_bits = [f'{roll} {damage_type}' for roll, damage_type in self.damage]
		if self.or_damage:
			damage_text = ' or '.join(damage_bits)
		else:
			damage_text = ', '.join(damage_bits)
		more_text = ' and more' if self.additional else ''
		return f'{self.name}, {plus}{self.bonus} to hit, {damage_text}{more_text}'

	def add_text(self, text):
		"""
		Add further explanatory text to the attack. (None)

		Parameters:
		text: The extra explanatory text. (str)
		"""
		self.additional = '{}\n\n{}'.format(self.additional, text)

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
		# Handle fumbles.
		if hit_roll == 1:
			total = 0
			text = 'Fumble'
		# Handle hits.
		elif hit_roll == 20 or hit_roll + total_bonus >= target.ac + target.ac_mod:
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
			target.hp = max(0, target.hp - total)
			print(f'{target.name.capitalize()} has {target.hp} hit points left.')
			# Create the text description.
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
	attack: The creature's attack actions. (dict of str: Attack)
	bonuses: The creature's ability bonuses. (dict of str: int)
	condtions: Any conditions affecting the creature, with timers. (list of tuple)
	cr: The creature's challenge rating. (int)
	features: Non-action features of the creature. (dict of str: str)
	hp: The creature's current hit points. (int)
	hp_max: The creature's maximum hit points. (int)
	hp_roll: The roll specification to determine the creature's hit points. (str)
	hp_temp: The creature's temporary hit points. (int)
	init_bonus: The creature's initiative bonus. (int)
	initiative: The creature's current combat priority. (int)
	language: The languages the creature can speak. (str)
	legendary: Legendary actions the creature can take. (dict of str: str)
	other_speeds: The creature's non-walking speeds, if any. (str)
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
	_parse_hp: Parse the creature's hit points. (None)
	_parse_languages: Parse the creature's languages. (None)
	_parse_legendary: Parse one of the creature's legendary actions. (None)
	_parse_saves: Parse the creature's saving throw bonuses. (None)
	_parse_skills: Parse the creature's skill bonuses. (None)
	_parse_size: Parse the creature's size, type, sub-type, and alignment. (None)
	_parse_speed: Parse the creature's movement speed. (None)
	attack: Attack something. (tuple of int, text)
	combat_text: Text representation for their turn in combat. (str)
	copy: Create an independent version of the creature. (Creature)
	init: Roll initiative for the creature. (int)
	save: Make a saving throw. (tuple of int, bool)
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
		# !! refactor
		# Set the creature's name.
		self.name = node.name.strip()
		self.name_regex = re.compile(r'\*\*{}e?s?\*\*'.format(self.name), re.IGNORECASE)
		# Set the creature's default attributes.
		self.ac = 10
		self.ac_mod = 0
		self.abilities = {'str': 10, 'dex': 10, 'con': 10, 'int': 10, 'wis': 10, 'cha': 10}
		self.actions = {}
		self.attacks = {}
		self.bonuses = {'str': 0, 'dex': 0, 'con': 0, 'int': 0, 'wis': 0, 'cha': 0}
		self.conditions = []
		self.description = ''
		self.features = {}
		self.hp_roll = '20d12'
		self.hp = 140
		self.hp_max = 140
		self.hp_temp = 0
		self.init_bonus = 0
		self.initiative = 0
		self.legendary = {}
		self.reactions = {}
		self.saves = self.bonuses.copy()
		self.size = 'Medium'
		self.skills = {skill: 0 for skill in self.skill_abilities}
		self.speed = 30
		self.other_speeds = ''
		self.type = 'unknown'
		# Set the Tracking variables.
		abilities = False
		last_key = ''
		last_dict = None
		# Loop through the node content.
		for node in node.children:
			if hasattr(node, 'lines'):  # if it has lines then it is a TextNode (avoids circular import)
				for line in node.lines:
					# Check for abilities.
					if abilities:
						if line[1] != '-':
							self._parse_abilities(line)
							abilities = False
					# Check for the starting size line.
					elif line[:5] in self.sizes:
						self._parse_size(line)
					# Check for non-standard features.
					elif line.startswith('***'):
						blank, title, text = line.split('***')
						last_dict, last_key = self._parse_feature(title, text)
					# Check for standard features.
					elif line.startswith('**'):
						blank, title, text = line.split('**')
						last = getattr(self, self.two_stars.get(title, '_parse_feature'))(title, text)
						if last is not None:
							last_dict, last_key = last
					# Check for starting to check for abilities.
					elif line.startswith('| STR'):
						abilities = True
					# Append loose paragraphs to the last feature found.
					elif line.strip():
						last_dict[last_key] = '{}\n\n{}'.format(last_dict[last_key], line)
			else:
				# !! Try to refactor these all into one.
				# !! Otherwise descriptions are only found after actions, not reactions/legendary actions.
				# Search through the actions section.
				if node.name.strip() == 'Actions':
					for child in node.children:
						for line in child.lines:
							# Handle named actions.
							if line.startswith('***'):
								last_dict, last_key = self._parse_action(line)
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
							# Handle named actions.
							if line.startswith('***'):
								last_dict, last_key = self._parse_reaction(line)
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
							# Check for the legendary actions.
							if line.startswith('**'):
								last_key = self._parse_legendary(line)
							# Check for loose paragraphs.
							elif line.strip():
								# Add to previous legendary actions.
								if last_key:
									new_text = '{}\n\n{}'.format(self.legendary[last_key], line)
									self.legendary[last_key] = new_text
								# Assume the first one describes legendary actions in general.
								else:
									self.legendary['Legendary Actions'] = line

	def __repr__(self):
		"""Debugging text representation. (str)"""
		return f'<Creature {self.name}, {self.size} {self.type}>'

	def __str__(self):
		"""Human readable text representation. (str)"""
		text = f'{self.name}; {self.hp}/{self.hp_max}'
		if self.conditions:
			text = '{}; {}'.format(text, ', '.join(self.condtions))
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
		self.ac_text = parts[1] if len(parts) > 1 else ''

	def _parse_action(self, line):
		"""
		Parse one of the creature's actions. (None)

		Parameters:
		line: The line of text with an action. (str)
		"""
		blank, name, text = line.split('***')
		if 'Attack:*' in line:
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

	def _parse_legendary(self, line):
		"""
		Parse one of the creature's legendary actions. (str)

		Parameters:
		line: The line of text with a legendary action. (str)
		"""
		blank, name, text = line.split('**')
		self.legendary[name] = text[1:].strip()
		return name

	def _parse_reaction(self, line):
		"""
		Parse one of the creature's actions. (None)

		Parameters:
		line: The line of text with an action. (str)
		"""
		blank, name, text = line.split('***')
		self.reactions[name] = text[1:].strip()
		return self.reactions, name

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

	def attack(self, target, name, advantage = 0, temp_bonus = 0):
		"""
		Attack something. (tuple of int, text)

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
		lines = [self.name]
		if self.conditions:
			lines.append(', '.join(self.conditions))
		lines.append('')
		# Set up speed/hp section.
		speed_text = f'Speed: {self.speed} ft.'
		if self.other_speeds:
			speed_text = f'{speed_text}; {self.other_speeds}'
		lines.append(speed_text)
		lines.append(f'HP: {self.hp}/{self.hp_max}')
		lines.append('')
		# Set up features:
		if self.features:
			lines.append('Features:')
			for title, text in self.features.items():
				text = text.replace('\n\n', '\n      ')
				lines.append(f'   {title}: {text}')
			lines.append('')
		# Set up actions:
		if self.actions:
			lines.append(f'Actions:')
			for title, text in self.actions.items():
				text = text.replace('\n\n', '\n      ')
				lines.append(f'   {title}: {text}')
			lines.append('')
		# Set up attacks:
		lines.append('Attacks:')
		for letter, attack in zip(self.letters, self.attacks.values()):
			lines.append(f'   {letter}: {attack}')
		# Combine the lines.
		return '\n'.join(lines)

	def copy(self, name = ''):
		"""
		Create an independent copy of the creature. (Creature)

		Parameters:
		name: The name for the new creature. (str)
		"""
		if not name:
			name = self.name
		clone = Creature(DummyNode(name, []))
		clone.__dict__ = self.__dict__.copy()
		clone.name = name
		clone.hp = dice.roll(clone.hp_roll)
		clone.hp_max = clone.hp
		return clone

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

	def update_conditions(self):
		"""
		Update condition timers, and remove finished conditions. (None)
		"""
		for condition in self.conditions:
			condition[1] -= 1
		self.conditions = [condition for condition in self.conditions if condition[1]]

# A fake header node for creating blank creatures.
DummyNode = collections.namedtuple('DummyNode', ('name', 'children'))
