"""
text.py

Text for the Egor DM Assistant.

Constants:
BONDS: Possible personality bonds. (list of str)
CLASSES: The names of the character classes. (list of str)
EXTREME_COLD: A warning message for low temperatures. (str)
EXTREME_HEAT: A warning message for high temperatures. (str)
FLAWS: Possible personality flaws. (list of str)
GOALS: Possible personality goals. (list of str)
HEAVY_PRECIPITATION: A warning for heavy rain or snow. (str)
HELP_CONDITIONS: Summaries of the various conditions. (str)
HELP_GENERAL: The general help text for Egor. (str)
HELP_SIGHT: Help text for vision and cover. (str)
IDEALS: Possible personality ideals. (list of str)
STRONG_WIND: A warning about high winds. (str)
TRAITS: Possible persoanlity traits. (list of str)
"""

BONDS = ['Duty to their students', 'Family first', 'Fear of someone they hurt', 'Forbidden love', 
	'Has a treasured possession', 'Helps those who help him', 'Indebted to generous person', 
	'Indebted to horrible person', 'Indebted to mentor', 'Indebted to an old friend', 'Lost their family', 
	'Lost their love', 'Loyalty to allies', 'Loyalty to friends', 'Loyal to their nation', 
	'Loyal to their people', 'Loyalty to their school', 'Loyalty to their sovreign', 
	'Must outshine their rival', 'Needs family approval', 'Needs to undo a wrong they did to someone', 
	'Never fail a loved one again', 'Protective of friends', 'Protecting secret knowledge', 
	'Protects their loved ones', 'Revenge upon a person who abused their power',
	'Revenge upon those who cast them out', 'Revenge upon those who destroyed their work', 
	'Revenge upon those who destroyed their homeland', 'Revenge upon those who killed someone they loved', 
	'Revenge upon those who stole from them', 'Treasures their allies', 'Treasures their friends', 
	'Owes their life to a foster parent', 'Wanted by an enemy', 'Wanted by the law', 
	'Wanted by someone powerful', 'Works for the common folk', 'Works for the orphans', 
	'Works to preserve an ancient text', 'Works for their temple or god']

CLASSES = ['Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue', 
	'Sorceror', 'Warlock', 'Wizard']

EXTREME_COLD = """
WARNING: Extreme cold while temperatures are below 1F. Characters must make a 
   DC 10 Constitution save or gain one level of exhaustion every hour. The
   save is not required for characters with cold resistance, cold immunity,
   cold weather gear, or a racial heritage adapted to cold temperatures.
"""

EXTREME_HEAT = """
WARNING: Extreme heat while temperatures are above 99F. Characters must make a 
   Constitution save (DC 5 for the first hour, +1 every hour after that) or 
   gain one level of exhaustion every hour. Characters in medium armor, heavy
   armor, heavy clothing have disadvantage on the save. The save is not 
   required for characters with fire resistance, fire immunity, access to
   water, or a racial heritage adapted to hot temperatures.
"""

FLAWS = ['Alcohol addict', 'Angry and violent', 'Blabber mouth', 'Blunt', 'Blinded by a sense of destiny', 
	'Bloodthirsty', "Can't back down from being called a coward", "Can't keep a secret worth shit", 
	"Can't lie worth shit", "Can't stand criticism", "Can't stand insults", "Can't stand losing arguments", 
	'Compulsive liar', 'Constantly chases beauty', 'Conspiracy theorist', 'Coward', 
	'Coward against stronger forces', 'Deflects blame onto others', 'Desparate for the rare and unique', 
	'Dislikes bathing', 'Does not trust others', 'Dogmatic', 'Drug addict', 'Easily distracted', 
	'Elitist', 'Everyone is beneath me', 'Foot in mouth disease', 'Foul mouthed', 'Gambling addict', 
	'Glutton', 'Greedy', 'Has a hated enemy', 'Hates plans and planning', 'Haunted by their past', 
	'Incredibly intolerant', 'Jealous of those better than them', 'Kleptomaniac', 'Lazy', 
	'Likes a good brawl', 'Little respect for those on a different path', 'Loose spender', 
	'Loves to hurt those in authority', 'Might makes right', 'Needs power to conquer fear', 'Neat freak', 
	'Never backs down', 'Never forgets a grude', 'No faith in allies', 'Obsessive collector', 'Paranoid', 
	'Predator/prey mentality', 'Prefers unfair fights', 'Prefers well bred society', 'Proud', 'Reckless', 
	'Rude', 'Sarcastic and insulting', 'Single-minded pursuit of goals', 'Snobbish about art', 
	'Snobbish about food', 'Suspicious of outsiders', 'Suspicious of strangers', 
	'The world revolves around them', 'Thinks they know best', 'Those who died were weak, and deserved it', 
	'Too many secrets', 'Trusts authority too much', 'Trusts people of the same religion too much', 
	'Unreliable', 'Very close-minded', 'Very judgemental, even of themselves', 'Vicious gossip', 
	'Will abandon others to save themselves']

GOALS = ['Get out of poverty', 'Find the answer to a particular question', 'Knowledge is power', 
	'My own ship', 'My own tavern', 'My own tower', 'Prevent others from having to live the life they did', 
	'Regain something stolen from them', 'Running from a scandalous past', 
	'Searching for that special someone', 'Seeks beauty', 'Seeks enlightenment', 'Seeks glory in battle', 
	'Seeks knowledge', 'Seeks fame', "Seeks power in their organization's hierarchy", 
	'Seeks redemption for a horrible crime', 'Self improvement through knowledge', 
	'Trying to win the love of a particular person', 'Wants a noble title', 
	'Wants to be the best in their field', 'Wants to bring change to the world', 'Wants to make a family', 
	'Wants to make people happy', 'Wants to make something of themselves', 
	'Wants to prove themselves to the doubters', 'Wants to uphold ancient traditions']

HEAVY_PRECIPITATION = """
WARNING: An area with heavy precipitation is lightly obscured, and sight
   preception checks are at disadvantage. If it is raining, hearing 
   perception checks are also at disadvantage. Heavy rain also extinguishes
   open flames.
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

You can generate random NPC names with the name command, and random NPC
personalities with the personality command.
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

IDEALS = ['Avoids hurting the poor', 'Beauty is truth', 'Believes they have a destiny to fulfill', 
	"Can't stand bullies", 'Community', 'Death to tyrants', 'Do not meddle in the affairs of others', 
	'Duty first', 'Eat the rich', 'Evil must be destroyed', 'Fair days pay for a fair days work'
	'Life is not fair, but we should make it fair', 'Follows the dictates of their deity', 
	'Follows their own way', 'Follows the ideals of a folk hero', 'Freedom is the most important thing', 
	'History must be preserved', 'Honesty is the best policy', 'Know yourself', 'Honor is life', 
	'Nature must be preserved', 'Never forget where you came from', 'Never leave anyone behind', 
	'No limits', 'Orders are meant to be obeyed', 'People deserve dignity and respect', 'Security is peace', 
	'Selflessly works for others', 'Steal from the rich and give to the poor', 'Strong work ethic', 
	'The low shall be lifted and the high shall fall', 'The strong must protect the weak', 
	'The world changes and we must adapt to the changes', 'To thine own self be true', 'Values bold action', 
	'Values creativity', 'Works for the redemption of others']

STRONG_WIND = """
WARNING: Ranged attacks and hearing perception checks are at disadvantage. Open
   flames are extinguished, fog is dispersed, natural flight is impossible. All
   flying creatures must land at the end of their turn or fall. Consider the 
   possibility of sandstorms or tornados. Sandstorms give disadvantage to sight
   perception checks.
"""

TRAITS = ['Absent minded', 'Always has a backup plan', 'Always helps those in trouble', 
	'Always has a relevant proverb/maxim.', 'Always has a relevant story', 'Always thinks things through', 
	'Always very calm', 'Appreciates a cutting insult', 'Believes disaster is coming', 'Bibliophile', 
	"Can't leave things unfinished", "Can't refuse a challenge", 'Confident in themselves', 
	'Constantly falling in love', 'Constantly lectures', 'Constantly quotes religious texts', 
	'Constantly tells jokes', 'Crude sense of humor', 'Curious', "Don't you know who I am?", 
	'Egalitarian', 'Fashionista', 'Fiddles with things constantly', 'Flatterer', 'Follows their gut', 
	'Food insecurity', 'Frugal', 'Gets bored easily', 'Good a mediating disputes', 
	'Gravitates toward complicated solutions', 'Habitually nervous', 'Has no time for wealth or manners', 
	'Hides when nervous', 'Idolizes a religous figure', 'Incredibly tolerant', 
	'Isolated, not used to dealing with people', 'Kind hearted', 'Logical and rational', 
	'Loves a good mystery', 'Loves gossip', 'Mercurial, changes moods constantly', 
	'Never tell me the odds', 'Oblivious to ettiquette and fashion', 'Opportunistically religious', 
	'Perfectionist', 'Prefers animals to people', 'Prefers doing to thinking', 'Polite and respectful', 
	'Possessed by wanderlust', 'Rarely speaks', 'Refuses to depend on others', 'Reliable', 
	'Scruffy looking', 'Socially awkward', 'Superstitious, constantly sees omens', 'Talks a lot',
	'Unshakeable optimism', 'Uses big words', 'Very empathetic', 'Very friendly', 'Very generous', 
	'Very used to fine living', 'Wants to be the center of attention', 'Wants to know how things work', 
	'Work hard, play hard']
