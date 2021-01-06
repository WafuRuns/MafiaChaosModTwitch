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

| Command           | Aliases      | Privileges  | Description                                                 |
|-------------------|--------------|-------------|-------------------------------------------------------------|
| !chaos_start      | !cstart      | Broadcaster | Starts sending effects to Chaos Mod                         |
| !chaos_end        | !cend        | Broadcaster | Stops sending effects to Chaos Mod (use after game crashes) |
| !chaos_help       | !chelp       | Anyone      | Shows help for voting                                       |
| <1-3>             |              | Anyone      | Submits a vote for the next effect                          |
| !chaos_poll       | !cpoll       | Moderator   | Starts posting polls and collecting votes                   |

## What's makejson.py for?

This file will create a new effects list from the [sheet of effects](https://docs.google.com/spreadsheets/d/1O-RrihWUizSNoTArYNuGz7bja_0ewbpXMjyf5FijBf4). You shouldn't be using this unless you're making changes to Chaos Mod.

## License
All of my code in this repository is public domain.
