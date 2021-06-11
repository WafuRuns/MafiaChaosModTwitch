# MafiaChaosModTwitch
Twitch bot for controlling Chaos Mod for Mafia: The City of Lost Heaven

## Installation
If you're looking to just play the mod, you'll need the Twitch version of Chaos Mod by WRP_Beater. You can find it in [Resources on speedrun.com](https://www.speedrun.com/mafia_ce/resources). Next, you should download the newest version of this bot in [Releases](https://github.com/KawaiiWafu/MafiaChaosModTwitch/releases) and extract it anywhere. Next, you'll need to fill in the login.json file, you can use Notepad to do it.

* IRC_TOKEN — After you've created the application (see CLIENT_ID below), use [Twitch Chat OAuth Password Generator](https://twitchapps.com/tmi/) to get the OAuth token.
* CLIENT_ID — You can get this ID from [Twitch Console](https://dev.twitch.tv/console), you first need to create an application. Make sure OAuth Redirect URLs is `http://localhost` and Category is Chat Bot. The Client ID should display when clicking the link with the application name.
* NICK — Name of the bot account (if you're using your stream account for this, enter your account name)
* PREFIX — Prefix that should be used to trigger commands (! by default)
* CHANNEL — Name of your Twitch account where bot will function

Finally, you save this file, start your game and then start the bot (as an Administrator!). To confirm it works, use any of the available bot commands in your Twitch chat.

## Commands

| Command      | Aliases | Privileges  | Description                                                 |
|--------------|---------|-------------|-------------------------------------------------------------|
| !chaos_start | !cstart | Moderator   | Starts sending effects to Chaos Mod                         |
| !chaos_end   | !cend   | Broadcaster | Stops sending effects to Chaos Mod (use after game crashes) |
| !chaos_help  | !chelp  | Anyone      | Shows help for voting                                       |
| <1-3>        |         | Anyone      | Submits a vote for the next effect                          |
| !chaos_poll  | !cpoll  | Moderator   | Starts posting polls and collecting votes                   |
| !chaos_setup | !csetup | Moderator   | Saves chaos mod settings from the game                      |
| !chaos_multi | !cmulti | Anyone      | Shares BASE64 code for sharing chaos effects                |

# Info for developers

## What's makejson.py for?

This file will create a new effects list from the [sheet of effects](https://docs.google.com/spreadsheets/d/1O-RrihWUizSNoTArYNuGz7bja_0ewbpXMjyf5FijBf4). You shouldn't be using this unless you're making changes to Chaos Mod.

## Interaction with the game

Interaction with the game is done by injecting into the game's memory. The bot changes or reads values of Tommy's attributes, this way, the game can react to these values and vice versa. This is the list of all attributes that we might or do use.

| Attribute    | Base     | Offset 1 | Offset 2 | Offset 3 | Offset 4 | Offset 5 | Usage                                             |
|--------------|----------|----------|----------|----------|----------|----------|---------------------------------------------------|
| inGame       | 0x2F94BC |          |          |          |          |          | Determines if the game is loading                 |
| Strength     | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x640    | No usage                                          |
| Health       | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x644    | No usage                                          |
| HealthHandL  | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x648    | No usage                                          |
| HealthHandR  | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x64C    | No usage                                          |
| Reactions    | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x658    | Effect toggles (1–16)                             |
| Speed        | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x65C    | No usage                                          |
| Aggressivity | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x660    | Effect toggles (17–32)                            |
| Intelligence | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x664    | Effect toggles (33–48)                            |
| Shooting     | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x668    | No usage                                          |
| Sight        | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x66C    | Effect toggles (49–64)                            |
| Hearing      | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x670    | Effect cooldown and duration, bot activation flag |
| Driving      | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x674    | Determines the effect to be used                  |
| Mass         | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x678    | No usage                                          |
| Morale       | 0x2F9464 | 0x54     | 0x688    | 0x4      | 0x44     | 0x67C    | No usage                                          |

## License
All of my code in this repository is public domain.
