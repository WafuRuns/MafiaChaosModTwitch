from twitchio.ext import commands
from pymem import Pymem
from pymem.exception import ProcessNotFound
import asyncio
import json
import sys
import websockets.legacy.client
import base64

class Bot(commands.Bot):
    def __init__(self, login, multi_code):
        multi_code_decoded = str(base64.b64decode(multi_code))[2:][:-1].split(',')
        super().__init__(token=login['IRC_TOKEN'],
                         client_id=login['CLIENT_ID'],
                         nick=login['NICK'],
                         prefix=login['PREFIX'],
                         initial_channels=[multi_code_decoded[0]])
        self.channel = multi_code_decoded[0]
        self.bot_name = multi_code_decoded[1]
        self.broadcaster = login['CHANNEL']
        self.sleep_task = None
        self.toggles = multi_code_decoded[2]
        self.duration = float(multi_code_decoded[3])
        self.cooldown = int(multi_code_decoded[4])
        self.effect_id = None

    async def event_ready(self):
        print(f'[INFO] Reading from channel {self.channel}')
        print(f'[INFO] Reacting to bot {self.bot_name}')
        print(f'[INFO] Toggles: {self.toggles}')
        print(f'[INFO] Duration: {self.duration}')
        print(f'[INFO] Cooldown: {self.cooldown}')
        print('[INFO] Started Chaos Mod')
        print(f'[WARN] Go to Vincenzo in the options map and set it to {self.duration}!')
        try:
            p = Pymem('Game.exe')
        except ProcessNotFound:
            print('[ERROR] Game is not running')
            return
        base = p.process_base.lpBaseOfDll
        pointer = base + 0x2F9464
        while True:
            while not self.effect_id:
                await asyncio.sleep(0.25)
            while True:
                await asyncio.sleep(0.25)
                try:
                    inGame = p.read_int(base + 0x2F94BC)
                    if not inGame:
                        val = p.read_int(pointer)
                        for i in (0x54, 0x688, 0x4, 0x44):
                            val = p.read_int(val + i)
                        p.write_float(val + 0x674, self.effect_id)
                        self.effect_id = None
                        self.sleep_task = asyncio.create_task(self.effect_cooldown(self.cooldown))
                        await asyncio.wait({self.sleep_task})
                        break
                except:
                    print('[WARN] Couldn\'t inject. If your game crashed, use !cend, restart game, wait for "Ended Chaos" message, then !cstart')
        print('[INFO] Ended Chaos Mod')

    async def effect_cooldown(self, cooldown):
        await asyncio.sleep(int(cooldown))

    async def event_message(self, message):
        if message.author.name.lower() == self.bot_name.lower():
            if 'Using effect:' in message.content:
                self.effect_id = float(message.content.split(': ')[1])
        await self.handle_commands(message)

def create_login():
    login = {}
    login['CHANNEL'] = input('Enter your Twitch name: ')
    login['NICK'] = input('Enter your Twitch bot name (same as your Twitch name if using only 1 account): ')
    if login['CHANNEL'] != login['NICK']:
        print('You are using 1 account for the bot and 1 for the stream. Do all of the things below as the bot account!')
    login['PREFIX'] = input('Enter your command prefix (!, $, ., etc.): ')
    print('Go to https://dev.twitch.tv/console and Register Your Application (Category must be Chat Bot, Redirect URLs must be http://localhost)')
    login['CLIENT_ID'] = input('Click the application name, copy the Client ID, paste it here: ')
    login['IRC_TOKEN'] = input('Go to https://twitchapps.com/tmi/, copy the token, paste it here: ')
    with open('login.json', 'w') as json_file:
        json.dump(login, json_file)

try:
    with open('login.json') as json_file:
        login = json.load(json_file)
except FileNotFoundError:
    print('[ERROR] login.json file was not found')
    create_login()
    input('Done. Relaunch the bot.')
    sys.exit(0)

print('[INFO] If your bot doesn\'t work, delete login.json file and start this program again')
print('[INFO] You always have to run this as administrator')
multi_code = input('Enter the streamer\'s !cmulti code: ')
bot = Bot(login, multi_code)
bot.run()
