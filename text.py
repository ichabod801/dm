"""
text.py

Text for the Egor DM Assistant.

Constants:
HELP_CONDITIONS: Summaries of the various conditions. (str)
HELP_GENERAL: The general help text for Egor. (str)
HELP_SIGHT: Help text for vision and cover. (str)
"""

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
they can be loaded by using the set command. Once loaded, your campaign files
can be searched with the campaign command. You can define name formats in the
Names chapter of your campaign documents, and then use the name command to
generate random NPC names for different cultures and genders.

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

HELP_SIGHT = """
Lightly obscured: Disadvantage on Perception checks relying on sight. Includes
   dim light, patch fog, and moderate foliage.
Heavily obscured: Creatures are blinded when looking into this area. Includes
   darkness, opaque fog, and dense foliage.

Bright light: Most creatures can see normally.
Dim light (shadows): Creates a lightly obscured area. Includes twilight or a
   bright moon.
Darkness: Creates a heavily obscured area.

Blindsight: Can perceive surroundings without relying on sight, up to a given
   radius.
Darkvision: Within range, dim light counts as bright light and darkness counts
   as dim light. You can't see color with darkvision.
Truesight: Can see in normal and magical darkness, can see invisible
   creatures, automatically detects visual illusions as makes all saves 
   against them, perceives the true form of shapeshifters and things trans-
   formed by magic. Can also see into the ethereal plane.

Half cover: Grants a +2 bonus to AC and Dexterity saves. Half cover = half
   the body blocked. Includes low walls, large furniture, a creature, or
   a thin tree.
Three-quarters cover: Grants +5 bonus to AC and Dexterity saves. Includes
   arrow slits and tree trunks.
Total cover: Can't be targetted directly by an attack or spell. Must be
   completely concealled.
"""