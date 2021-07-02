# Campaign Files

The Egor systems allows for customization through campaign files. Campaign files are markdown formatted text files in a special folder. All the files for a given campaign need to be in the same folder. If you don't know what markdown formatting is, do a web search for 'markdown'. Note that all markdown files are assumed to start with a single '#' header.

In the Egor system, you load the campaign files by setting the campaign folder with the set command.

```
EGOR >> set campaign portal

The campaign at portal has been loaded.
```

The above just sets to the portal folder in the dm folder that the Egor system resides in. That is, 'portal' should be replace with a path to your campaign folder **relative to** the dm folder egor.py is in.

If you want files to be read, they need to follow a particular naming convention. The name of the file should be 'XX.chapter-name.md'. XX should be a two digit number, 'chapter-name' can be replaced with the name of the "chapter" in your campaign book, and the extension must be '.md'.

The campaign files can be used to search for information you have written about you campaign, add homebrew monsters to Egor's combat tracker, add more information on player characters to the system, add random name generation for non-player characters (NPCs), and to add custom calendars to the Egor system. There are sections below covering each of these uses.

## Searching Campaign Files

The campaign files are loaded using the same system that the Source Reference Document (SRD) is loaded. You can access them with the campaign command (alias 'camp') the same way you use the srd command.

```
EGOR >> camp $zaz

1: Deities of Quartzgard > Zaz, God of Death
2: Quartzgard, City of the Sphinx > Major Organizations > The Cult of Zaz

Which section would you like to view (return for none)? 2

### The Cult of Zaz

The priests of Zaz have built up a presence here to try and undermine the pilgrimage  route. They are very 
much underground, and work covertly and obliquely to disrupt things. They are wary of  Khafra, and avoid 
direct confrontation. They generally work to make things tough for the pilgrims. However, a priestess of 
Suranah name Leshanna Amakiir (elven cleric 5) has noticed the higher crime rate against pilgrims, and is 
starting to investigate it.

The high priest of Zaz in the area, and the head of the cult, is Morn Beaverdam (human cleric 10). His 
cover is a prominent merchant in spices, with a shop named Morning Spices on the fourth tier. Not known to 
many is that he also owns Sharp’s Weaponry on the second tier. He is vying for a seat on the council of 
merchants, and is vocally opposed to the influence the Temple of Suranah has in city affairs. His plan is 
to get on the council and then use blackmail and selective assassination to shift things in favor of 
splitting the religious role of Khafra from the Lord Mayorship.

The ostensible high priest of Zaz in Quartzgard is Ivor of Pistilsky (human cleric 5). He runs a small 
temple on the second tier. He knows of Morn’s presence in the city, and follows any instructions Morn 
gives him. However, he is not privy to Morn’s plans. Morn considers Ivor to be a risk, and has plans in 
place for Ivor accidentally dying in a ritual, followed by the ascension of a lesser priest.
```

Plain searches search for an exact match with a header. Searches starting with a '$' do a regular expression search on the headers. Searches starting with a '+' do a regular expression search on the text. Headers in markdown are lines beginning with a '#'.

## Homebrew Monsters

If you have created any homebrew monsters you can put stat blocks for them in the campaign files. The parser I have is pretty picky, and I want to work on that, but for the mean time you need to be careful with the formatting. Generally, you can just copy from the SRD files and modify the text. If you run into problems, check this section for details that the parser looks for.

Every chapter file is searched for stat blocks. Any that are found are added to the list of creatures available for combat in the Egor system. The exception is any chapter whose top level header (the single '#' header at the start of the file) is 'Player Characters'. Egor loads those into the player character tracking.

Here is the Orc statblock in markdown, to use as an example.

```
## Orc

*Medium humanoid (orc), chaotic evil*

**Armor Class** 13 (hide armor)

**Hit Points** 15 (2d8+6)

**Speed** 30 ft.

| STR     | DEX     | CON     | INT    | WIS     | CHA     |
|---------|---------|---------|--------|---------|---------|
| 16 (+3) | 12 (+1) | 16 (+3) | 7 (-2) | 11 (+0) | 10 (+0) |

**Skills** Intimidation +2

**Senses** darkvision 60 ft., passive Perception 10

**Languages** Common, Orc

**Challenge** 1/2 (100 XP)

***Aggressive***. As a bonus action, the orc can move up to its speed toward a hostile creature that it 
can see.

###### Actions

***Greataxe***. *Melee Weapon Attack:* +5 to hit, reach 5 ft., one target. *Hit:* 9 (1d12+3) slashing 
damage.

***Javelin***. *Melee or Ranged Weapon Attack:* +5 to hit, reach 5 ft. or range 30/120 ft., one target. 
*Hit:* 6 (1d6+3) piercing damage.
```

### Detecting the Stat Block

The parser searches for headers that are followed by a line starting with a size. It only checks headers of less than sixth level (less than six '#'s). The text for the line following the header needs to start with `*Tiny`, `*Small`, `*Medium`, `*Large`, `*Huge`, or `*Gargantuan`. The size line should also have a creature type after the size, a comma, and then an alignment.

### Armor Class

The line with armor class needs to start with two asterisks (`**`). The first word after `**Armor Class**` should be an integer of the armor class. All other words after that are assumed to be describing the armor worn.

### Hit Points

The line with hit points needs to start with two asterisks (`**`). The first word after `**Hit Points**` should be the average hit points for the creature, or the max hit points for a player character. This should be followed by a space and a description of the hit dice in parentheses. This should be identifiable as a dice roll to Egor, as he will use it to roll hit points for creatures in combat.

### Speed

The line with the creature's speed needs to start with two asterisks (`**`). The first word after `**Speed**` should be the integer ground speed of the creature. This is typically followed by ' ft.', but that is not necessary. If there is a comma after that, anything after the comma is assumed to be alternate speeds for the creature, such as climb, swim, or fly speeds.

### Abilities

Abilities have to be done in a pipe table. Specifically, the parser looks for '| STR' to start the pipe table. Then it searches for a line without a dash ('-') as the second character. It assumes that line has the abilities in the standard order, separated by pipes. Between the pipes, the first word should be an integer for the ability score. Ability bonuses in the stat block are ignored, Egor calculates the bonus from the score. That bonus is used as the default bonus for all skills and saves. The dexterity bonus is used for initiative.

### Skills

The line with skills needs to start with `**Skills**`. The text after `**Skills**` should be skills with bonuses, each pair separated by a comma (like 'Sleight of Hand +5, Stealth +5'). Incorrect skill names will be entered into the creature's data incorrectly, and will not be usable by the skill command.

### Saves

The line with skills needs to start with `**Saves**`. The text after `**Saves**` should be saves (using three letter ability names) with bonuses, each pair separated by a comma (like 'Str +8, Wis +1'). Incorrect ability names will be entered into the creature's data incorrectly, and will not be usable by the save command.

### Senses

The line with senses needs to start with `**Senses**`. However, no processing is done on this line, it is just copied into the creature's data.

### Languages

The line with languages needs to start with `**Languages**`. However, no processing is done on this line, it is just copied into the creature's data.

### Challenge Rating

The line with the challenge rating and experience points needs to start with `**Challenge**`. Egor can read fractional challenge ratings (like the orc's 1/2), but stat blocks may print strangely if you use a fractional CR without a 1 for a numerator. The experience points for the creature should be the second word in parentheses after the challenge rating. While commas normally mess up Egor's reading of integers, they can be used here.

Note that Egor ignores the challenge rating, it is not used by any of the commands (at the moment). The experience points are totaled up for creatures who are killed in combat, either through auto-kill at 0 hp or with the kill command. The total can be accessed with the xp command.

### Other Features

Any line that starts with three asterisks (`***`) or two asterisks and an unknown name (not one of the ones listed above) is just stored as a feature of that creature. The text emphasized by the asterisks is assumed to be the name of the feature, and the rest of the text is stored as the description of the features. If you have two features with the same name, the second one will overwrite the first.

#### Multi-Line Paragraphs

If a feature has mutliple lines (paragraphs) explaining it, the parser will correctly put those lines together as long as the following lines do not start with asterisks.

### Actions vs. Attacks

After a header named 'Actions', every line starting with three asterisks (`***`) is parsed as an action or an attack. If the line contains `Attack*`, Egor attempts to parse it as an attack (see below). Otherwise, it is copied into the creatures actions.

#### Attacks

The meat of the attack description is assumed to be after the first instance of `Attack*` in the attack's text. Egor does classify attacks, based on the presence of the words Melee, Ranged, and/or Spell in the text of the attack. However that classification isn't really used by the system.

The attack bonus is assumed to be the first word after the first instance of `Attack*`. Next is the hit text, which is considered the text between `*Hit:* ` (note the trailing space) and the next period. Any words in the hit text that start with '(' and end with ')' are treated as damage rolls. That means there can be no spaces in the damage roll text. `(2d8+4)` will be correctly parsed as a damage roll. `(2d8 + 4)` will not. Yeah, this needs to be fixed, and it's on the list.

If there are multiple damages, the will all be added together, but specified differently. Something like 'Hit (15 + 9) for 16 points; 6 points of piercing damage, 10 points of necrotic damage'. However, if the word 'or' is in the hit text, the lower damage is given before the break down. This is common for versatile weapons, which give different damage one-handed versus two-handed. Those attack will read like 'Hit (18 + 4) for 3 points; 4 points of slashing damage or 3 points of slashing damage'. You will need to have some understanding of the attack, and possibly adjust the damage as needed. An alternative when making homebrew creatures or NPC stat blocks is to split versatile weapons into two attacks.

Anything after the hit text is saved as additional hit effects, like needing to save after a successful unamred strike from a wight. Note that if the hit text has no damage rolls, it is put in the additional effects as well. This is common with spell attacks.

### Reactions and Legendary Actions

Two other special headers are recognized by Egor: 'Reactions' and 'Legendary Actions'. These are handled similarly, but slightly differently. Reactions are lines starting with three asterisks (`***`) and legendary actions are lines starting with two asterisks (`**`). As with features, whatever is emphasized is taken as the name, and the rest of the text is the description. Lines starting without the required number of asterisks are further expanation of the previous reaction/legendary effect.

Again, this is rather arbitrary and picky. It's based off the markdown SRD I am using. For campaign files I would like it to be more general, just emphasized text at the start of a line, including using the alternate markdown syntax of underscores instead of asterisks. That is also on the list.

## Player Characters

When Egor scans the campaign files, the stat blocks are stored in his 'zoo' of creatures you can use in combat. However, if the text for the header node at the start of the document is 'Player Characters', Egor stores all of the stat blocks in that chapter in his 'pcs' dictionary. Anything in the pcs dictionary is put into every combat, with a question asking for the initiative roll.

## Random Names

Egor has a name command that can generate random names for different combinations of species/culture and gender. If you have a campaign file titled 'Names' or 'names' (not counting the leading number or the extension, so '12.names.md' counts), that will be read as a specification for generating these random names.

Each species or culture should have a second level header (two octothorpes/`##`) that gives the name of the culture. The text under that header should have lines starting with text emphasized by two asterisks (`**`). The emphasized text is the name of a name part. After the emphasized text should be a comma separated list of possible names for that name part. Both the species/cultures and name parts should be single words or hypenated words ('Orc' or 'Half-Elf').

After the name parts are specified, there should be a series of level three headers (three octothorpes/`###`). These are the 'genders'. As with the cultures, species, and name parts, these should be single words or hyphenated words. I put genders in quotes because the names you are creating may not be categorized by gender, but by something else like occupation. I just call the second level of categorization gender for convenience.

Under each gender header is a format. A format is text with name parts in braces ({}). A simple examples would be '{male} {last}'. That would create a name with a random male name part, followed by a space, followed by a random last name part. You might then have another gender with the name format '{female} {last}'. You could also have a name format like '{male} du{last}'. Then every man's last name would start with 'du'.

Note that your name parts in the gender formats better match up to the name parts you specified in the first section. Otherwise there will be an error when you try to generate random names. The name parts in the formats need to be lower case, but they can be upper case when they are listed.

A gender can have more than one name format. Each one should be listed on a separate line, starting with a number in brackets ([]). The numbers are the percent chance that the given name format will be used. For example:

```
### Female

[30] {female} {adjective}{noun}

[70] {female} {clan}
```

This gives a thiry percent chance that wome will have a descriptive clan name using a random noun and adjective, and a seventy percent chance that they will have a standard clan name. Note that here you have a female name part, and a female gender. That is fine, Egor can keep track of them separately.

Only use the same name part twice if you want it to repeat. For example, say you want a patronymic (a name based on the father's name). You might think to try '{male} {clan}, son of {male}'. However, the way Egor works, the patronymic will always be the same as the first name. To fix this, just copy the list of male names, and make another name part called 'father'. Then '{male} {clan}, son of {father}' will (generally) give a different name for the patronymic.

## Calendars

Egor has some support for calendars in addition to basic time-in-the-dungeon. If you have a campaign file titled 'Calendar' or 'calendar' (not counting the leading number or the extension, so '18.calendar.md' counts), that will be read as a specification for generating a calendar. If your campaign has a calendar, you can use the date command in Egor to see what the date is for the current day. Note that times in Egor assume a year that is 365 days long. Your calendar will override that.

### Types of Calendars

Egor supports two types of calendars: fractional calendars and deviation calendars. Both have a list of months, which can have different numbers of days in them. 

A fractional calendar has a fractional year length and an overage month. That year length keeps getting added up, and when the fractional part first exceeds 0.5, a day is added to the overage month. Say you have a year lenght of 365.2422. The first year you have 365.2422. 0.2422 is under 0.5, so no extra day. The second year you add again, 730.4844. The third year you have 1095.7266. Now you are over 0.5, so an extra day is added to the overage month. Note that the fourth year total is 1460.9688. That is also over 0.5, but Egor knows the overage day has already been added, and waits for the fractional part to cycle past 0.0 again.

A deviation calendar has an integer year length and a set of deviations. Each deviation is based on a modulus of the year. So you might have a 365 day year month, and a deviation that says if the year modulus 4 is 0, add an extra day to the second month. You can have multiple deviations, and they can undo each other. So you might have a second deviation say that if they year modulus 100 is 0, set the second month to the normal number of days. This is (partially) how the Gregorian calendar works.

### Specifying a Calendar

Here is a sample calendar:

```
# Andellan 

The calendar used in the world of Andella.

**Days in Year** 384

## Months

| Month        | Days |
|--------------|------|
| Early Spring | 32   |
| Mid-Spring   | 32   |
| Late Spring  | 32   |
| Early Summer | 32   |
| Mid-Summer   | 32   |
| Late Summer  | 32   |
| Early Fall   | 32   |
| Mid-Fall     | 32   |
| Late Fall    | 32   |
| Early Winter | 32   |
| Mid-Winter   | 32   |
| Late Winter  | 32   |

## Deviations

Mid-Spring, 33, 12, 0

Mid-Summer, 33, 12, 3

Mid-Fall, 33, 12, 6

Mid-Winter, 33, 12, 9

Mid-Summer, 32, 36, 27
```

The first header gives the name of the calendar. After that you can put in a description of the calendar. Egor ignores this. What Egor looks for is `**Days in Year**`. If a line starts with that text, the rest of the line should be the number of days in the year. If the number has a decimal part, the calendar is assumed to be a fractional calendar. For a fractional calendar, you also need a line starting with `**Overage Month**`. The rest of that line should be the name of the month that gets an extra day. If the days in the year is an integer and no overage month is specified, Egor assumes the calendar is a deviation calendar.

Next is a second level header (two octothorpes, `##`) named Months. This section needs a pipe table. The first column of the table should be the month names in order, and the second column should be the normal days in that month. The days for each month should be an integer, even with fractional calendars.

If you are specifying a deviation calendar, you need a section with a second level header titled 'Deviations'. Each line is a deviation. Deviations give a month name, a new number of days for that month, a value to divide the year by, and a remainder that triggers the deviation. For example, the first deviation listed above is 'Mid-Spring, 33, 12, 0'. That means 'set Mid-Spring to 33 days long if the year divided by 12 is 0'.

You will see there are two triggers for Mid-Summer in the Andellan calendar. Triggers will be checked in the order they are listed, so 'Mid-Summer, 33, 12, 3' will be checked before 'Mid-Summer, 32, 36, 27'. Now, if year mod 36 is 27, year mod 12 is 3. So once every 36 years they will both trigger, the first one setting Mid-summer to 33 days, and the second one setting it back to 32 days.

You can give multiple remainders for a trigger. So you could have a deviation 'Mid-Summer, 33, 36, 3, 15'. That would give Mid-Summer 33 days if the year mod 36 is either 3 or 15. That is equivalent to the two Mid-Summer deviations specified above.

### Cycles

Calendars can contain other cycles, like weekdays or moons. Egor supports two types of cycles within calendars: fractional cycles and static cycles. Each one is made up of a list of named periods within the cycle. A particular named moon might be a named period, or a given weekday might be a named period.

#### Fractional Cycles

Fractional cycles have the same number of days per period, and that number has a fractional part. As with fractional years, the fractional parts add up until they go over 0.5. At that point, whatever the current period is gets an extra day, not a specified period. 

If the total length of a fractional cycle is longer than the calendar year it is in, it resets every year. It doesn't reset on the first day of the year, but the first new cycle each year is the first cycle listed. That means that the last cycle listed may not happen every year.

Fractional cycles are specified with a line starting with **period length**, that contains the length of each period. Then there is a pipe table with the names of the periods. For example:

```
### Moons

**period length** 24.68

| Moon     |
|----------|
| Ent      |
| Rain     |
| Flower   |
| Faerie   |
| Fire     |
| Buck     |
| Dragon   |
| Bright   |
| Harvest  |
| Ranger   |
| Beaver   |
| Skeleton |
| Cold     |
| Wolf     |
| Ghost    |
| Death    |
```

#### Static Cycles

Statics cycles don't change. Each period has a set number of days and that never changes. This is for things like weeks, where each weekday is a period, with a length of one day.

To specify a static cycle, just give a pipe table where the first column is the name of the period, and the second column is the number of days in the period. For example:

```
### Fatangdays

| Fatangday | Days |
|-----------|------|
| Pushday   | 1    |
| Secday    | 1    |
| Mootday   | 1    |
| Seeday    | 1    |
| Darkday   | 1    |
| Cleanday  | 1    |
| Grinday   | 1    |
| Godsday   | 1    |
```

### Formats

Calendars can have formats, as well. These can be referenced when using the date command in Egor. For example, if you have a format named 'long', using 'date long' in Egor will give you the date in that format. Just using 'date' without specifying a format gives you the date in the default format. You can specify a default format, but if you don't, the default default format is '{month-name} {day-of-month}', which might give something like 'Late Spring 5' in the Andellan calendar.

The formats are text, with date parts in braces ({}). What you can put in your braces depends on how you have defined your calendar. Certain date parts are always available:

- day-of-month: The number of the current day in the current month.
- day-of-year: The number of the current day in the year.
- month-name: The name of the current month.
- month-number: The number of the current month in the list of months.
- year: The number for the year.

All numbers start with one, so the first day-of-year is 1, and the second month in the month list has the month-number 2.

Each cycle has a name, taken from the header node that starts the cycle definition. So the example cycles above are named Moons and Fatangdays. Each period has date parts, based on the lowercase version of their name. To get the date parts for a cycle, replace 'name' in the below date parts with the lower case name of the cycle:

- name-day: The number of the day in the full cycle.
- name-number: The number of the cycle since the start of the calendar.
- name-period: The name of the current period within the cycle.
- name-period-day: The number of the day within the current period.

As an example, the format '{fatangdays-period}, {day-of-month} {month-name}, day {moons-period-day} of the {monns-period} moon.' might come out as 'Godsday, 8 Early Winter, day 25 of the Skeleton moon.'
