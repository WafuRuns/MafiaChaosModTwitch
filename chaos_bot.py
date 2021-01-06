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

    async def event_ready(self):
        try:
            with open('effects.json') as json_file:
                self.data = json.load(json_file)
        except FileNotFoundError:
            print("[ERROR] effects.json file was not found")
            input()
            sys.exit(0)

    @commands.command(name='chaos_start', aliases=['cstart'])
    async def chaos_start(self, ctx):
        if ctx.author.name == self.broadcaster:
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
                effect_id = float(effect['id'])
                while not self.stopped:
                    await asyncio.sleep(1)
                    try:
                        inGame = p.read_int(base + 0x2F94BC)
                        if not inGame:
                            val = p.read_int(pointer)
                            for i in (0x54, 0x688, 0x4, 0x44):
                                val = p.read_int(val + i)
                            p.write_float(val+0x648, effect_id)
                            p.write_float(val+0x64C, 1.0)
                            self.blocked.append((effect, datetime.now() + timedelta(seconds=effect['duration'])))
                            self.new_poll = True
                            self.sleep_task = asyncio.create_task(asyncio.sleep(45))
                            await asyncio.wait({self.sleep_task})
                            break
                    except:
                        print('[WARN] Couldn\'t inject. If your game crashed, use !cend, restart game, wait for "Ended Chaos" message, then !cstart')
            await ctx.send('Ended Chaos.')
            print('[INFO] Ended Chaos Mod')
    
    def random_effects(self, count):
        while True:
            now = datetime.now()
            sample = random.sample(self.data['effects'], count)
            for i in sample:
                for y in self.blocked:
                    if i['id'] == y[0]['id']:
                        if now < y[1]:
                            continue
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
                    effects_text = ", ".join(effects)
                    await ctx.send(effects_text)
                    await asyncio.sleep(30)
                    winner = max(self.votes.items(), key=operator.itemgetter(1))[0]
                    self.queue.append(sample[winner-1])
                    self.votes.clear()
                    self.voted.clear()
                    await ctx.send("Voting ended.")

    @commands.command(name='chaos_end', aliases=['cend'])
    async def chaos_end(self, ctx):
        if ctx.author.name == self.broadcaster:
            self.stopped = True
            try:
                for process in psutil.process_iter():
                    if "Game" in process.name():
                        process.terminate()
            except:
                print('[ERROR] Game is already dead or you don\'t have administrator privileges')
            try:
                self.sleep_task.cancel()
            except AttributeError:
                print("[WARN] Trying to end when not running")

    @commands.command(name='chaos_help', aliases=['chelp'])
    async def chaos_help(self, ctx):
        await ctx.send('Use !chaos_vote <1-3> or !cvote <1-3> to choose the next effect.')

try:
    with open('login.json') as json_file:
        login = json.load(json_file)
except FileNotFoundError:
    print("[ERROR] login.json file was not found")
    input()
    sys.exit(0)

bot = Bot(login)
bot.run()
