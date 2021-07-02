# dm.py

The dm.py package is a command line interface to a set of tools for dungeon masters of Dungeons & Dragons 5th Edition. 

## Current Status

I have finished the first pass of coding. I have been using this version in my campaign for about a month now, but I would like a few more months of smoke testing before sending it out into the world.

## Basic Usage

If you have saved the files in a folder in your python path, you can start the system with an import:

```
import dm
dm.run()
```

You can also do that if you are in the folder above the dm folder. Or you can navigate to the dm folder, and use Python to run the run.py file.

```
(base) C:\Users\spam\dm>python run.py
```

See the WALK_THROUGH.md for examples of using the system. You can also use the help command in the system for an overview of the system's functionality.

## Features

- Dice roller;
- Combat tracker, with SRD and homebrew monsters, large combat options, attacks, saves, and skill checks;
- Set up encounters, including random encounters;
- Game time tracker;
- Note tracker, with tags;
- Searching of the Source Reference Document;
- Custom campaign files with searching, homebrew monsters, PC data, random name generation, and calendars;
- Random NPC personalities;
- Random weather by climate and season;
- XP tracking;
- Annoying, obsequious, deformed servant voice that you can turn off.

## Documentation

There is a lot of documentation in the system's help command. In addition, there is the WALK_THROUGH.md file with some examples of using the system, and CAMPAIGN_FILES.md file with details on setting up custom campaign files.

## Copyright

Everything in the srd folder is copyright 2015 by Wizards of the Coast. See the README and legal documents in that folder. The markdown versions of the SRD were made by B.A. Umberger in cooperation with Juxtagames, LLC (See https://github.com/Umbyology/OGL-SRD5). I did change some formating necessary to load the monsters correctly.

All of the files outside of the srd are copyright 2021 by Craig O'Brien. The are is licensed under the GPLv3 license. See the LICENSE.txt file for details.