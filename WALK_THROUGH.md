This is a quick walk through of a simple session of dm.py, to give you a basic idea of how to use the system.

If you have save the files in a folder in your python path, you can start the system with an import:

```
import dm
dm.run()
```

You can also do that if you are in the folder above the dm folder. Or you can naviate to the dm folder, and use Python to run the run.py file.

```
(base) C:\Users\spam\dm>python run.py
```

Once you get it started you will see an introduction message like this:

```
Welcome, Master of Dungeons.
I am Egor, allow me to assist you.

Yes, master? 
```

You can use the roll command to roll dice, although if Egor cannot figure out what command you are trying to use, he will assume you are trying to roll dice.

```
Yes, master? roll 3d6

11

Yes, master? 2d20kh1

10
```

(The kh1 keeps the one highest die, so 2d20kh1 is rolling with advantage.)

You can search the Source Reference Document with the srd command.

```
Yes, master? srd invisibility


#### Invisibility

*2nd-level illusion*

**Casting Time:** 1 action

**Range:** Touch

**Components:** V, S, M (an eyelash encased in gum arabic)

**Duration:** Concentration, up to 1 hour

A creature you touch becomes invisible until the spell ends. Anything the target is wearing or carrying is 
invisible as long as it is on the target's person. The spell ends for a target that attacks or casts a 
spell.

***At Higher Levels***. When you cast this spell using a spell slot of 3rd level or higher, you can target 
one additional creature for each slot level above 2nd.
```

The default is to search the headers of the SRD. If you preface the search with a $, Egor will do a regular expression search on the headers. If you preface the search with a +, he will do a regular expression search of the text. If multiple matching sections are found, Egor will list the matching sections and let you choose which one to view.

```
Yes, master? srd $grappl

1: CUSTOMIZATION > Feats > Grappler
2: COMBAT > Making an Attack > Melee Attacks > Grappling
3: GAMEMASTERING > Conditions > Grappled

Which scroll would you like to peruse, master? 3

## Grappled

- A grappled creature's speed becomes 0, and it can't benefit from any bonus to its speed.
- The condition ends if the grappler is incapacitated (see the condition).
- The condition also ends if an effect removes the grappled creature from the reach of the grappler or 
grappling effect, such as when a creature is hurled away by the *thunder-wave* spell.
```

If you are tired of the obsequious deformed helper tone that Egor uses, you can change this with the set command:

```
Yes, master? set voice dry

Standard voice settings restored.

EGOR >>
```

If you want to use the combat tracker, it's best to enter your player's characters so that they can be automatically used. This can be done with the pc command.

```
EGOR >> pc add flint

What is their initiative bonus? 2
What is their armor class? 21
How many hit points do they have? 81
What are their ability scores (comma separated)?

EGOR >> pc add claw claw

What is their initiative bonus? 3
What is their armor class? 15
How many hit points do they have? 54
What are their ability scores (comma separated)?
```

Notice that I didn't add the ability scores. Really what you need is the armor class, so other creatures can attack them correctly. You don't need hp unless you don't trust your player's to track them. You don't need the initiative bonus if they are going to be rolling their own initiatives.

You can get a lot more detail about the player characters into the system by using the campaign files. See the 'Campaign Files' documentation for more information on that. Also note that any campaign files you do create can be searched just like the SRD. To do so, use the campaign command rather than the srd command.

Now that we have PCs, we can start combat with the initiative command.

```
EGOR >> initiative

What is the initiative for Flint? 9
What is the initiative for Claw-claw?
Other combatant name: orc
Number of those combatants: 3
Other combatant name: tentaclor
Number of those combatants: 1
What is the initiative bonus for tentaclor (hit enter for typo in creature name)? 4
Other combatant name:

It is now Round 1
-------------------
claw claw
-------------------
Speed: 30 ft.
AC: 15
HP: 54/54
-------------------
Attacks:
-------------------

2: orc-3; AC 13; 16/16
3: flint; AC 21; 81/81
4: orc-2; AC 13; 14/14
5: tentaclor; AC 10; 130/130
6: orc-1; AC 13; 13/13
```

There's a lot going on here, which is typical of D&D combat. Note that I entered an initiative for Flint, but not for Claw Claw. If you don't enter one, the system will roll it for you. This is useful if there are NPCs with the party that you are running. Also note how 'claw claw' became 'Claw-claw'. That's just how the system stores things, you can still reference her with 'claw claw' or 'Claw-claw'.

Next I entered two creatures for the combat: three orcs and a tentaclor. Egor asked me for the initiative bonus for the tentaclor, but not the orcs. That's because the orcs are in the SRD, but the tentaclor is a homebrew monster of mine that Egor doesn't know anything about. Now, as with the player characters, I could put the full stats for the tentaclor into the campaign files, and then Egor would know what a tentaclor's initiative is.

It would also know what dice to roll for the tentaclor's hit points. You can see that the three orcs all have different hit points (the two numbers after their name), because Egor knows that orcs have 2d8+6 hit points.

The current actor is Claw Claw, and she is shown with an abbreviated stat block. This is even more abbreviated since we entered her with the pc command and not the campaign files. That's okay, she's a PC, just tell her player it's their time to act. Let's say the player goes up to orc-3, rolls and attack, and gets 12 damage. This is where the hit command comes in.

```
EGOR >> hit orc-3 12

orc-3 now has 4 HP.
```

Boom. Now Claw Claw is done, and it's the orc's turn. Use the next command to get to the next combatant in the initiative order.

```
EGOR >> next

-------------------
orc-3
-------------------
Speed: 30 ft.
AC: 13
HP: 4/16
-------------------
Features: Aggressive
Attacks:
   A: Greataxe, +5 to hit, 1d12+3 slashing
   B: Javelin, +5 to hit, 1d6+3 piercing
-------------------

3: flint; AC 13; 81/81
4: orc-2; AC 21; 14/14
5: tentaclor; AC 10; 130/130
6: orc-1; AC 13; 13/13
1: claw claw; AC 15; 54/54
```

We can see a bit more information for the orc, since it was fully loaded from the SRD. But it's still a pretty abbreviated stat block (I found the full stat block was too confusing in combat). But we can see the full stat block with the stats command, which we might want to do if we have forgotten what the Aggressive feature does.

```
EGOR >> stats orc-3

## orc-3

*Medium humanoid (orc), chaotic evil*
**Armor Class** 13 ((hide armor))
**Hit Points** 4/16 (2d8+6)
**Speed** 30 ft.

| STR     | DEX     | CON     | INT    | WIS     | CHA     |
|---------|---------|---------|--------|---------|---------|
| 16 (+3) | 12 (+1) | 16 (+3) | 7 (-2) | 11 (+0) | 10 (+0) |

**Senses** darkvision 60 ft., passive Perception 10
**Languages** Common, Orc
**Challenge** 1/2.0 (100 XP)
**Aggressive**. As a bonus action, the orc can move up to its speed toward a hostile creature that it can see.
Attacks:
   A: Greataxe, +5 to hit, 1d12+3 slashing
   B: Javelin, +5 to hit, 1d6+3 piercing
```

Note that we got the stats for that particular orc, orc-3, with just four HP left. At any time you can use the stats command to pull up the general stat block for any creature in the SRD or your campaign files.

In any case, it's time to attack Claw Claw, using the attack command.

```
EGOR >> attack claw-claw greataxe

Claw claw has 50 hit points left.
Hit (12 + 5) for 4 points of slashing damage
```

Note that in this case, you need to put the hyphen into claw-claw. Commands with multiple arguments generally parse using spaces, so the dash clarifies that claw-claw is one thing, the name of a PC.

Egor tells us the roll and the attack bonus, and the damage with the damage type. It also tells us the remaining hit points for the target. If the attack had missed, it would still tell us the attack roll and bonus, unless it was a fumble. It will also calculate the damage on a critical hit. You can also specify an attack having advantage/disadvantage or a sitational bonus. You can find the details with 'help attack'.

The first problem is that typing `attack claw-claw greataxe` is going to get old fast, especially when trying to run a quick combat. Many of the commands have aliases to make them easier to type. You can find them in the help text for the command, in parentheses after the first line. So we can find that the alias for the attack command is '@'. Next, combatants can be refered to by their place in the initiative order. So instead of 'claw-claw', we could just use '1'. Finally, you'll note that the attacks for a creature have letters before them. You can use these to reference the attacks. So `attack claw-claw greataxe` can be written as `@ 1 a`, which is much easier to type. Also, the 'A' attack for a creature is considered to be the default. So you could write it as `@ 1`. Note that if you are specifying (dis)advantage or a situational bonus, you have to specify the attack.

The second problem comes when Claw Claw's player says "I'm blade singing right now. Did you take into account my +3 int bonus to AC?" No, actually we didn't. And we can see from the attack text that it wouldn't have hit (12 + 5 < 18). Now, as noted, we could use a situational bonus here, and do the attack as `@ 1 a -3`. But that's a pain, and we need to undo the 4 points of damage.

```
EGOR >> heal 1 4

claw claw now has 54 HP.

EGOR >> ac 1 3

claw claw's armor class is now 15 + 3 = 18
```

The heal command is the opposite of the hit command, and gives hp to the creature indicated (again we are using Claw Claw's initiative order of 1 as a quick way to identify her). The ac command sets an armor class modifier for the specified combatant. It can easily be turned off with `ac 1 0`.

Now that we have fixed that, let's move on to Flint's attack.

```
EGOR >> n

-------------------
flint
-------------------
Speed: 30 ft.
AC: 21
HP: 81/81
-------------------
Attacks:
-------------------

4: orc-2; AC 13; 14/14
5: tentaclor; AC 10; 130/130
6: orc-1; AC 13; 13/13
1: claw claw; AC 18; 54/54
2: orc-3; AC 13; 4/16

EGOR >> hit 2 8

orc-3 now has 0 HP.
orc-3 has been removed from the initiative order.
```

First, note that we used the alias 'n' for the 'next' command to get to Flint, the next combatant in the initiative order. Next, when we hit orc-3 (identified with his initiative order of 2) for 8 points, it dropped to 0 HP, and was automatically removed from the initiative order. Egor will do this for monsters, but not for player characters (to give them time to heal each other, or in case you are not closely tracking their HP). You can use the set command to turn this off for all combatants (`set auto-kill false`). If you want to force something out of the initiative order otherwise, you can use the kill command.

Now, say Flint has another attack. He might go after orc-2, using 4 to identify him. Be careful of this, because when orc-3 is removed from the initiative order, that order changes. If at any point you need clarification of the current initiative order, you can see it again with the show command.

```
EGOR >> show

-------------------
flint
-------------------
Speed: 30 ft.
AC: 21
HP: 81/81
-------------------
Attacks:
-------------------

3: orc-2; AC 13; 14/14
4: tentaclor; AC 10; 130/130
5: orc-1; AC 13; 13/13
1: claw claw; AC 18; 54/54
```

And now we can see that orc-2 is now identified by initiative order 3.

After the combat is over, you might want to make some notes for future reference. You can do this with the note command, which has the alias '&'.

```
EGOR >> & Flint killed his first orc. | combat

The note was added to the system for later storage.

EGOR >> & Don't forget Claw Claw's bladesinger bonus to ac. | player

The note was added to the system for later storage.
```

I used pipes when making these notes. The text after the pipes is the tag (or tags) for the note. This can be useful later when you use the study command to review the notes.

```
EGOR >> study player

Don't forget Claw Claw's bladesinger bonus to ac.
```

You might also want to add 10 minutes to your tracking of the time in game for the combat and the clean up afterwards.

```
EGOR >> time 10

Year 1, Day 1, 6:10
```

You can use the alarm command to set up warnings for you, like when the players' torch is going to burn out, or when the next orc patrol is going to happen.

When the players get out of the orc cave, they might want to know what the weather is.

```
EGOR >> weather temperate fall

The temperature ranges from a low of 50F to a high of 63F.
There is a light wind today.
There is no rain today.
```

Note that the weather command will also give you warnings of game effects for severe weather. For example:

```
EGOR >> weather temperate fall

The temperature ranges from a low of 70F to a high of 83F.
There is little to no wind today.
There is heavy rain today.
WARNING: An area with heavy precipitation is lightly obscured, and sight
   preception checks are at disadvantage. If it is raining, hearing
   perception checks are also at disadvantage. Heavy rain also extinguishes
   open flames.
```

There's a lot more to the system. Just typing `help` will give you a general overview, with a list of all the commands and help topics. I've tried to make sure there is decent help text for each command. There are also help topics for things you might find on a DM's screen, like conditions, cover, and sight. Also check out the Campaign Files documentation, which has info on more details PC stat blocks, stat blocks for homebrew creatures, setting up a calendar, and setting up different cultures with different names.

Finally, you can use the quit command (alias 'q') to leave the Egor system.

```
EGOR >> q

Save changes to the Egor system (y/n)? 
```

Egor can save changes you've made to the system. This includes PCs you have added, notes you have made, settings you have changed, and the current time and any alarms. Note that it does not save the current initiative order. All this is saved in the dm.dat file in the folder with the program. The format is meant to be somewhat human readable, so you can go in and pull out any notes you made and copy them into some other application you are using for long term tracking.