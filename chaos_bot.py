from twitchio.ext import commands
from pymem import Pymem
from pymem.exception import ProcessNotFound
import asyncio
import json
import random
import operator
import sys
import psutil
from datetime import datetime, timedelta
from math import floor

class Bot(commands.Bot):
    def __init__(self, login):
        super().__init__(irc_token=login['IRC_TOKEN'],
                         client_id=login['CLIENT_ID'],
                         nick=login['NICK'],
                         prefix=login['PREFIX'],
                         initial_channels=[login['CHANNEL']])
        self.data = {}
        self.blocked = []
        self.votes = {}
        self.voted = []
        self.queue = []
        self.new_poll = False
        self.stopped = False
        self.broadcaster = login['CHANNEL']
        self.sleep_task = None
        self.toggles = ''
        self.duration = 45
        self.cooldown = 6.0

    async def event_ready(self):
        try:
            with open('effects.json') as json_file:
                self.data = json.load(json_file)
        except FileNotFoundError:
            print('[ERROR] effects.json file was not found')
            input()
            sys.exit(0)

    async def effect_cooldown(self, cooldown, process, base):
        for _ in range(int(cooldown * 4)):
            process.write_float(base + 0x678, 0.0)
            await asyncio.sleep(0.25)

    @commands.command(name='chaos_setup', aliases=['csetup'])
    async def chaos_setup(self, ctx):
        if ctx.author.is_mod:
            try:
                p = Pymem('Game.exe')
                base = p.process_base.lpBaseOfDll
                pointer = base + 0x2F9464
                val = p.read_int(pointer)
                for i in (0x54, 0x688, 0x4, 0x44):
                    val = p.read_int(val + i)
                reactions = p.read_float(val + 0x658) / 0.7
                aggressivity = p.read_float(val + 0x660) / 0.6
                intelligence = p.read_float(val + 0x664) / 0.8
                sight = p.read_float(val + 0x66C)
                for i in (reactions, aggressivity, intelligence, sight):
                    self.toggles += bin(int(round(i)))[2:].zfill(16)[::-1]
                hearing = p.read_float(val + 0x670)
                self.cooldown = floor(hearing / 1000)
                self.duration = hearing - self.cooldown * 1000
                print(f'[INFO] Toggles set to: {self.toggles}')
                print(f'[INFO] Cooldown set to: {self.cooldown}')
                print(f'[INFO] Base duration set to: {self.duration}')
            except ProcessNotFound:
                print('[ERROR] Game is not running')
                return

    @commands.command(name='chaos_start', aliases=['cstart'])
    async def chaos_start(self, ctx):
        if ctx.author.is_mod:
            self.stopped = False
            await ctx.send('Started Chaos Mod.')
            print('[INFO] Started Chaos Mod')
            try:
                p = Pymem('Game.exe')
            except ProcessNotFound:
                print('[ERROR] Game is not running')
                return
            base = p.process_base.lpBaseOfDll
            pointer = base + 0x2F9464
            while not self.stopped:
                if not self.queue:
                    effect = self.random_effects(1)[0]
                else:
                    effect = self.queue[0]
                    self.queue.pop(0)
                effect_id = float(effect['id']*0.008)
                while not self.stopped:
                    await asyncio.sleep(0.25)
                    try:
                        inGame = p.read_int(base + 0x2F94BC)
                        if not inGame:
                            val = p.read_int(pointer)
                            for i in (0x54, 0x688, 0x4, 0x44):
                                val = p.read_int(val + i)
                            p.write_float(val + 0x678, 0.0)
                            p.write_float(val + 0x674, effect_id)
                            self.blocked.append((effect, datetime.now() + timedelta(seconds=effect['duration'] * self.duration * 15)))
                            self.new_poll = True
                            self.sleep_task = asyncio.create_task(self.effect_cooldown(self.cooldown, p, val))
                            await asyncio.wait({self.sleep_task})
                            break
                    except:
                        print('[WARN] Couldn\'t inject. If your game crashed, use !cend, restart game, wait for "Ended Chaos" message, then !cstart')
            await ctx.send('Ended Chaos.')
            print('[INFO] Ended Chaos Mod')
    
    def random_effects(self, count):
        valid_sample = False
        while not valid_sample:
            valid_sample = True
            now = datetime.now()
            sample = random.sample(self.data['effects'], count)
            for i in sample:
                if self.toggles[i['id'] - 1] == '0':
                    valid_sample = False
                    break
                for y in self.blocked:
                    if i['id'] == y[0]['id']:
                        if now < y[1]:
                            valid_sample = False
                            break
                        else:
                            self.blocked.remove(y)
        return sample

    async def event_message(self, message):
        if message.content[0].isnumeric():
            vote = int(message.content[0])
            if vote in range(1, 4):
                if message.author.name not in self.voted:
                    self.voted.append(message.author.name)
                    self.votes[vote] += 1
        await self.handle_commands(message)


    @commands.command(name='chaos_poll', aliases=['cpoll'])
    async def chaos_poll(self, ctx):
        if ctx.author.is_mod:
            self.new_poll = True
            while True:
                await asyncio.sleep(1)
                if self.new_poll:
                    self.new_poll = False
                    self.votes = {
                        1: 0,
                        2: 0,
                        3: 0
                    }
                    sample = self.random_effects(3)
                    effects = []
                    for i, effect in enumerate(sample):
                        effects.append(f"({str(i+1)}) {effect['name']}")
                    effects_text = ', '.join(effects)
                    await ctx.send(effects_text)
                    await asyncio.sleep(self.cooldown / 1.5)
                    winner = max(self.votes.items(), key=operator.itemgetter(1))[0]
                    self.queue.append(sample[winner-1])
                    self.votes.clear()
                    self.voted.clear()
                    await ctx.send('Voting ended.')

    @commands.command(name='chaos_end', aliases=['cend'])
    async def chaos_end(self, ctx):
        if ctx.author.name == self.broadcaster.lower():
            self.stopped = True
            try:
                for process in psutil.process_iter():
                    if 'Game' in process.name():
                        process.terminate()
            except:
                print('[ERROR] Game is already dead or you don\'t have administrator privileges')
            try:
                self.sleep_task.cancel()
            except AttributeError:
                print('[WARN] Trying to end when not running')

    @commands.command(name='chaos_help', aliases=['chelp'])
    async def chaos_help(self, ctx):
        await ctx.send('Type a number between 1 and 3 to choose the next effect.')

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
bot = Bot(login)
bot.run()
