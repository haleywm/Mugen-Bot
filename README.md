# Mugen Bot

A small bot I made to practice python and allow people to publically select random characters on a discord server.

Uses py-cord, as that is the best supported discord library at the time of writing, and python 3.10.

## Installation

First, install python 3.10. Then, install the dependancies using `pip install -r requirements.txt`.

Next, copy `default_config.json` to `config.json`. Edit the `"token": ""` section so that the empty quotes contain your bots token. (https://discordjs.guide/preparations/setting-up-a-bot-application.html#creating-your-bot walks through the process of creating a bot and getting the token.) You'll also want to add the bot that you create to any servers, the invite link can be gotten from this same area.

Next, customise the other settings as you'd like. This will primarily involve changing the names to something else, and changing the other numbers if you want. Note that there must be at least `characters_given` many characters in the list, and `characters_given` can't be higher than 24 due to limits with buttons on discord dialogue. (24 is a lot though so I'm not trying to work around this).

Next, start the bot using `python3 main.py` inside the folder, it will print any error messages that occur. Any servers containing the bot should now be able to use the `/get_characters` command to generate a list.
