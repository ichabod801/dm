"""
srd.py

Functions for reading the D&D SRD in markdown format.

Classes:
Node: A node in a document tree. (object)
HeaderNode: A header in a document tree. (object)
TextNode: A section of text in a document tree. (object)
SRD: A collection of information from the SRD. (object)
Table: A rollable table in a markdown document. (object)
"""

import collections
import os
import random
import re

from . import creature
from . import dice
from . import gtime

class Node(object):
	"""
	A node in a document tree. (object)

	Methods:
	add_child: Add a child node to the tree. (None)
	full_text: Get the full text of the header and it's children. (str)

	Overridden Methods:
	__init__
	"""

	def __init__(self):
		"""Set up the default Node attributes."""
		self.parent = None
		self.children = []

	def add_child(self, node):
		"""
		Add a child node to the tree. (None)

		Parameters:
		node: The child node to add. (Node)
		"""
		self.children.append(node)
		node.parent = self

	def full_text(self):
		"""Get the full text of the header and it's children. (str)"""
		parts = [str(self)]
		parts.extend(child.full_text() for child in self.children)
		return '\n\n'.join(parts)

class HeaderNode(Node):
	"""
	A header in a document tree. (object)

	Attributes:
	level: How general the header is, low being more general. (int)
	name: The name (text) of the header.

	Methods:
	full_header: Full location of the header in the chapter. (str)
	header_search: Search the children's headers for matches. (list of HeaderNode)
	text_search: Search the children's text for matches. (list of HeaderNode)

	Overridden Methods:
	__init__
	__repr__
	__str__
	"""

	def __init__(self, text):
		"""
		Set up the header's level and name. (None)

		Parameters:
		text: The text for the header. (str)
		"""
		super().__init__()
		markdown, space, self.name = text.partition(' ')
		self.level = len(markdown)

	def __repr__(self):
		"""Debugging text representation. (str)"""
		return f'<HeaderNode level {self.level}: {self.name}>'

	def __str__(self):
		"""Human readable text representation. (str)"""
		markdown = '#' * self.level if self.level else '#'
		return f'{markdown} {self.name}'

	def full_header(self):
		"""Full location of the header in the chapter. (str)"""
		# Get all of the names going up the parent chain.
		text = self.name
		parent = self.parent
		while parent is not None:
			text = f'{parent.name} > {text}'
			parent = parent.parent
		return text

	def header_search(self, terms):
		"""
		Search the children's headers for matches. (list of HeaderNode)

		Parameters:
		terms: The terms to search for. (Pattern or str)
		"""
		# Get the subheaders.
		sub_heads = [child for child in self.children if isinstance(child, HeaderNode)]
		# Search based on regular expression or text
		if isinstance(terms, str):
			matches = [child for child in sub_heads if terms.lower() == child.name.lower()]
		else:
			matches = [child for child in sub_heads if terms.search(child.name)]
		# Continue the search depth first.
		for child in sub_heads:
			matches.extend(child.header_search(terms))
		# Return the results.
		return matches

	def text_search(self, terms):
		"""
		Search the children's text for matches. (list of HeaderNode)

		Parameters:
		terms: The terms to search for. (Pattern or str)
		"""
		# Get the headers by type.
		sub_heads, texts = [], []
		for child in self.children:
			if isinstance(child, HeaderNode):
				sub_heads.append(child)
			else:
				texts.append(child)
		# Search any text children.
		matches = [child for child in texts if child.text_search(terms)]
		# Continue the search depth first.
		for child in sub_heads:
			matches.extend(child.text_search(terms))
		# Return the results.
		return matches

class TextNode(Node):
	"""
	A section of text in a document tree. (object)

	Attributes:
	lines: The lines of text in the section. (object)

	Methods:
	add_line: Add another line of text to the section. (None)
	full_header: Full location of the section in the chapter. (str)
	strip: Remove leading and trailing blank lines. (None)
	text_search: Search the text lines for matches. (bool)

	Overridden Methods:
	__init__
	__repr__
	__str__
	"""

	def __init__(self, text):
		"""
		Set up the text lines. (None)

		Parameters:
		text: The first line of text for the section. (str)
		"""
		super().__init__()
		self.lines = [text]

	def __repr__(self):
		"""Debugging text representation. (str)"""
		return f'<TextNode {len(self.lines)} lines ({self.lines[0][:20]}...)>'

	def __str__(self):
		"""Human readable text representation. (str)"""
		return '\n'.join(self.lines)

	def add_line(self, text):
		"""
		Add another line of text to the section. (None)

		Parameters:
		text: The next line of text for the section. (str)
		"""
		self.lines.append(text)

	def full_header(self):
		"""Full location of the section in the chapter. (str)"""
		# Use the parent header.
		return self.parent.full_header()

	def strip(self):
		"""Remove leading and trailing blank lines. (None)"""
		while not self.lines[0].strip():
			self.lines.pop(0)
		while not self.lines[-1].strip():
			self.lines.pop()

	def text_search(self, terms):
		"""
		Search the text lines for matches. (bool)

		Parameters:
		terms: The terms to search for. (Pattern or str)
		"""
		for line in self.lines:
			if terms.search(line):
				return True
		return False

class SRD(object):
	"""
	A collection of information from the SRD. (object)

	Attributes:
	chapters: The different files in the SRD. (dict of str: Node)
	headers: The header nodes in the document. (dict of str: list of HeaderNode)
	names: The name definitions in the document. (dict)
	pcs: The creatures from the Player Characters chapter. (dict of str: Creature)
	zoo: The creatures in the various chapters. (dict of str: Creature)

	Class Attributes:
	file_names: The names of the SRD files. (list of str)

	Methods:
	header_search: Search the chapters' headers for matches. (list of HeaderNode)
	parse_creatures: Parse a node for creatures. (None)
	parse_file: Parse a markdown file from the SRD. (None)
	parse_names: Parse a node for named lists. (None)
	parse_tables: Parse a node for a rollable table. (None)
	read_files: Read the files of the SRD. (dict of str:str)
	text_search: Search the children's text for matches. (list of HeaderNode)

	Overridden Methods:
	__init__
	"""

	file_names = ['01.races', '02.classes', '03.customization', '04.personalization', '05.equipment',
		'06.abilities', '07.adventuring', '08.combat', '09.spellcasting', '10.spells', '11.gamemastering',
		'12.treasure', '13.monsters', '14.creatures', '15.npcs']
	name_part_re = re.compile(r'\{(\w*)\}')

	def __init__(self, folder = 'srd'):
		"""
		Read in the SRD. (None)

		Parameters:
		folder: The local folder the SRD is stored in. (str)
		"""
		self.chapters = {}
		self.pcs = {}
		self.tables = {}
		self.zoo = {}
		self.calendar, self.name = None, None
		self.headers = collections.defaultdict(list)
		for name, lines in self.read_files(folder).items():
			self.chapters[name] = self.parse_file(lines)
		for chapter in self.chapters.values():
			self.parse_creatures(chapter)
			self.parse_tables(chapter)
		for character in self.pcs.values():
			character.pc = True
		if 'calendar' in self.chapters:
			self.calendar = gtime.parse_calendar(self.chapters['calendar'])
		if 'names' in self.chapters:
			self.parse_names(self.chapters['names'])

	def header_search(self, terms):
		"""
		Search the children's headers for matches. (list of HeaderNode)

		Parameters:
		terms: The terms to search for. (Pattern or str)
		"""
		# Do the header search on each chapter.
		matches = []
		for chapter in self.chapters.values():
			matches.extend(chapter.header_search(terms))
		return matches

	def get_name(self, culture, gender):
		"""
		Generate a random name based on the Names chapter. (str)

		Parameters:
		culture: The culture to generate a name for. (str)
		gender: The gender to generate a name for. (str)
		"""
		# Pull the data for that culture/gender.
		culture = self.names[culture]
		formats = culture['formats'][gender]
		format_index = random.randint(1, 100)
		for chance, gender in formats:
			if format_index <= chance:
				break
		# Generate random name parts for all possible genders.
		data = {key: random.choice(value) for key, value in culture.items() if key != 'formats'}
		# Apply the name parts to the gender format.
		return gender.format(**data)

	def parse_creatures(self, node):
		"""
		Parse a node for creatures. (None)

		Parameters:
		node: The node to parse for creatures. (HeaderNode)
		"""
		target = self.pcs if node.name.lower() == 'player characters' else self.zoo
		search = [node]
		while search:
			node = search.pop()
			if node.level < 5 and node.children:
				intro = node.children[0]
				if isinstance(intro, TextNode) and intro.lines[0][:5] in creature.Creature.sizes:
					try:
						monster = creature.Creature(node)
						target[monster.name.lower().replace(' ', '-')] = monster
					except:
						print(f'Error parsing creature {node.name}.')
				elif node.level < 4:
					search.extend([kid for kid in node.children if isinstance(kid, HeaderNode)])

	def parse_file(self, lines):
		"""
		Parse a markdown file from the SRD. (None)

		Parameters:
		lines: The lines of text from the file. (list of str)
		"""
		# Get the chapter title as a 0-level header node.
		root = HeaderNode(lines[0][1:])
		# Loop through the lines.
		parent = root
		text = None
		mode = 'search'
		for line in lines[2:]:    # skip the header with the chapter title.
			# When you have text, add to it until you get a header.
			if mode == 'text':
				if line.startswith('#'):
					mode = 'search'
					text.strip()
					parent.add_child(text)
				else:
					text.add_line(line)
			# Otherwise try to find headers and text.
			if mode == 'search':
				if line.startswith('#'):
					# Create a header node.
					header = HeaderNode(line)
					# Add it to the right parent.
					while header.level <= parent.level:
						parent = parent.parent
					parent.add_child(header)
					# Track it as the new parent.
					self.headers[header.name].append(header)
					parent = header
				elif line:
					# Create a text node and switch modes.
					text = TextNode(line)
					mode = 'text'
		if mode == 'text' and text not in parent.children:
			text.strip()
			parent.add_child(text)
		return root

	def parse_names(self, node):
		"""
		Parse a node for named lists. (None)

		Parameters:
		node: The node to parse for name lists. (HeaderNode)
		"""
		self.names = {}
		search = [node]
		while search:
			node = search.pop()
			if node.level == 2:
				# Second level nodes are name definitions.
				culture = node.name.lower()
				self.names[culture] = {'formats': {}}
				for child in node.children:
					# Get lists of names.
					if isinstance(child, TextNode):
						for line in child.lines:
							if line.startswith('**'):
								blank, tag, names = line.split('**')
								names = [name.strip() for name in names.strip(': ').split(',')]
								self.names[culture][tag.lower()] = names
					# Get formats.
					elif child.level == 3:
						gender = child.name.lower()
						self.names[culture]['formats'][gender] = []
						total = 0
						for line in child.children[0].lines:
							# Check for multiple formats with probabilities.
							if line.startswith('['):
								chance = int(line[line.index('[') + 1:line.index(']')])
								parts = line[line.index(']') + 1:].strip()
								total += chance
								self.names[culture]['formats'][gender].append((total, parts))
							elif line:
								self.names[culture]['formats'][gender].append((100, line))
			else:
				# All other nodes should be searched for second level nodes.
				search.extend([child for child in node.children if isinstance(child, HeaderNode)])

	def parse_tables(self, node):
		"""
		Parse a node for a rollable table. (None)

		Parameters:
		node: The node to parse for tables. (HeaderNode)
		"""
		# Seach the header tree.
		search = [node]
		while search:
			node = search.pop()
			for child in node.children:
				# Continue to search from headers.
				if isinstance(child, HeaderNode):
					search.append(child)
				# Scan for tables in text.
				else:
					mode = 'text'
					for line in child.lines:
						# Find tables by their header.
						if line.startswith('**Table'):
							mode = 'table'
							name = line[7:-2].strip('- \t')
						# Only scan ones with a roll for the first column.
						elif mode == 'table' and line.startswith('|'):
							if dice.TIGHT_REGEX.search(line[1:line.index('|', 2)]):
								mode = 'rollable'
								roll = line[1:line.index('|', 2)].strip()
								rows = []
							else:
								mode = 'text'
						# Store all of the text rows of the table
						elif mode == 'rollable' and line.startswith('|'):
							rows.append(line)
						# Create and store the table.
						elif mode == 'rollable':
							self.tables[name.lower()] = Table(name, roll, rows)
							mode = 'text'
					# Catch tables at the end of the text.
					if mode == 'rollable':
						self.tables[name.lower()] = Table(name, roll, rows)

	def read_files(self, folder = 'srd'):
		"""
		Read the files of the SRD. (dict of str:str)

		Parameters:
		folder: The local folder the SRD is stored in. (str)
		"""
		chapters = {}
		for file_name in os.listdir(folder):
			if file_name[:2].isdigit() and file_name.endswith('.md'):
				with open(f'{folder}/{file_name}', encoding = 'utf-8') as srd_file:
					chapters[file_name[3:-3]] = srd_file.read().split('\n')
		return chapters

	def text_search(self, terms):
		"""
		Search the children's text for matches. (list of HeaderNode)

		Parameters:
		terms: The terms to search for. (Pattern or str)
		"""
		# Do the header search on each chapter.
		matches = []
		for chapter in self.chapters.values():
			matches.extend(chapter.text_search(terms))
		return matches

class Table(object):
	"""
	A rollable table in a markdown document. (object)

	Attributes:
	name: The name of the table. (str)
	die_roll: The roll used to read the table. (str)
	rows: The possible results from the table. (list of tuple)

	Class Attributes:
	value_regex: A pattern for one or two dash-separated integers. (Pattern)

	Methods:
	roll: Generate a result from the table. (str)

	Overridden Methods:
	__init__
	"""

	value_regex = re.compile(r'\d+\-?\d*')

	def __init__(self, name, roll, rows):
		"""
		Finish parsing the table rows. (None)

		Parameters:
		name: The name of the table. (str)
		roll: The roll used to read the table. (str)
		rows: The rows of the table. (list of str)
		"""
		# Store the base attributes
		self.name = name
		self.die_roll = roll
		# Parse the text rows of the table.
		self.rows = []
		for row in rows:
			blank, value, result, *junk = row.split('|')
			# Handle ranges of values vs. single values
			if self.value_regex.search(value):
				if '-' in value:
					low, high = [int(word) for word in value.split('-')]
				elif value.strip().isdigit():
					low = int(value)
					high = low
				else:
					continue
			else:
				continue
			self.rows.append((low, high, result.strip()))

	def roll(self):
		"""Generate a result from the table. (str)"""
		value = dice.roll(self.die_roll)
		for low, high, result in self.rows:
			if low <= value <= high:
				break
		return result

if __name__ == '__main__':
	srd = SRD()
	chapters = list(enumerate(srd.chapters.values()))
	while True:
		print()
		for num, chapter in chapters:
			print(f'{num}. {chapter}')
		target = input('Enter chapter number: ')
		try:
			target = int(target)
		except ValueError:
			break
		else:
			node = chapters[target][1]
			while True:
				print()
				if isinstance(node, TextNode):
					print(node)
					input('Press enter to go back up: ')
					node = node.parent
				else:
					print(node.full_header())
					for num, child in enumerate(node.children):
						print(f'{num}: {repr(child)}')
					target = input('Enter node number: ')
					if target:
						node = node.children[int(target)]
					elif node.parent:
						node = node.parent
					else:
						break
