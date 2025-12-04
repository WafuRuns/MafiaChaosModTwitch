# MafiaChaosModTwitch
Twitch bot for controlling Chaos Mod for Mafia: The City of Lost Heaven

## Installation
If you're looking to just play the mod, you'll need the Twitch version of Chaos Mod by WRP_Beater. You can find it in [Resources on speedrun.com](https://www.speedrun.com/mafia_ce/resources). Next, you should download the newest version of this bot in [Releases](https://github.com/KawaiiWafu/MafiaChaosModTwitch/releases) and extract it anywhere. Next, you'll need to fill in the login.json (doesn't apply to shared clients, you don't need a bot if you only receive effects from someone's bot) file, you can use Notepad to do it.

* CLIENT_ID — You can get this ID from [Twitch Console](https://dev.twitch.tv/console), you first need to create an application. Make sure OAuth Redirect URLs is `http://localhost:4343/oauth/callback` and Category is Chat Bot. The Client ID should display when clicking the link with the application name.
* CLIENT_SECRET — You can get it in the same section by clicking the button for revealing the secret.
* BOT_ID — ID of the bot account (https://streamscharts.com/tools/convert-username)
* CHANNEL_ID — ID of the channel, can be the same as bot if you're the same account (https://streamscharts.com/tools/convert-username)
* PREFIX — Prefix that should be used to trigger commands (! by default)

When you first start the bot and have these things set up (remember the redirect URL is very important, otherwise it won't work), with the bot account logged in on Twitch (ideally in Incognito mode), go to http://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20user:bot%20channel:manage:polls&force_verify=true

Next, you need to authorize the bot for your account, this time you will use your regular Twitch account where you want the bot to operate, and then go to http://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20user:bot%20channel:manage:polls%20channel:bot&force_verify=true

**Sometimes this simply doesn't work, because Twitch keeps old information and redirects you incorrectly. To fix that, look at the URL in your browser, you will see a client ID which will be different from the one you're trying to use. Simply change it to one of your bot and this should work. This sometimes happens when you have multiple projects in the dev console.**

Finally, start your game and then start the bot (as an Administrator!). To confirm it works, use any of the available bot commands in your Twitch chat.

In the setup room, after setting all the settings, use !csetup command. Then go through the door, pause the game, use !cpoll and !cstart.

## Multi Installation

If you want to use shared effects, you don't need a bot. Twitch has changed some things and it's no longer possible to scan someone else's chat (and if you manage that, your bot account will soon be banned). This makes things harder and easier at the same time.

* You no longer need a bot if you just wanna get the same effects as the main player
* The main player needs a public IP or any tool that will allow you to connect, such as ZeroTier (**ZeroTier was the tested approach and it worked fine**)

I won't go into detail as to how to do the last step, there's a plenty of guides online.

**As the host:** You absolutely need to open port 1930 (haha) on your firewall for incoming connections. Again, very simple, use the first guide you can find. Or disable firewall altogether, *if you're brave enough*. In the setup room, you just click on Biff until it enables chat voting, then in the bot you enable sharing effects.

**As the client:** Just start the multi bot as administrator while your game is in the setup room, enter the host's IP (e.g. 192.168.1.100). It will tell you what effect duration to set at Vincenzo, then you go to Biff, set chat voting to enabled and don't care about anything else.

Feel free to contact me on Discord if you have any issues: wafuruns

## Troubleshooting

* If the game crashes for the client, there should be no issue. Just exit the bot, start it again the same way, go through the door, load last checkpoint.
* If the game crashes for the host, use !cend, start the game, setup everything in the setup room as it was, then use !cstart. If the bot crashes, all clients will have to restart their bots and the host will have to do the whole setup again.

## Commands

| Command      | Aliases | Privileges  | Description                                                 |
|--------------|---------|-------------|-------------------------------------------------------------|
| !chaos_start | !cstart | Moderator   | Starts sending effects to Chaos Mod                         |
| !chaos_end   | !cend   | Broadcaster | Stops sending effects to Chaos Mod (use after game crashes) |
| !chaos_poll  | !cpoll  | Moderator   | Starts posting polls and collecting votes                   |
| !chaos_setup | !csetup | Moderator   | Saves chaos mod settings from the game                      |

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
