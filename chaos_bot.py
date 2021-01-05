from twitchio.ext import commands
from pymem import Pymem
from pymem.exception import CouldNotOpenProcess
import asyncio
import json
import random
import operator
import sys
import psutil
import os
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
        self.old_pid = None

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
        if ctx.author.is_mod:
            self.stopped = False
            await ctx.send('Started Chaos Mod.')
            print('[INFO] Started Chaos Mod')
            try:
                p = Pymem()
                pid = None
                for process in psutil.process_iter():
                    if "Game" in process.name():
                        pid = process.pid
                if pid:
                    p.open_process_from_id(pid)
                    self.old_pid = pid
                else:
                    print('[ERROR] Game is not running')
                    return
            except CouldNotOpenProcess:
                print('[ERROR] Game is not running')
                return
            base = p.process_base.lpBaseOfDll
            pointer = base + 0x2F9464
            while True and not self.stopped:
                if not self.queue:
                    effect = self.random_effects(1)[0]
                    effect_id = float(effect['id'])
                else:
                    effect = self.queue[0]
                    effect_id = float(effect['id'])
                    self.queue.pop(0)
                while True and not self.stopped:
                    await asyncio.sleep(1)
                    try:
                        val = p.read_int(pointer)
                        for i in (0x54, 0x688, 0x4, 0x44):
                            val = p.read_int(val + i)
                        p.write_float(val+0x648, effect_id)
                        p.write_float(val+0x64C, 1.0)
                        self.blocked.append((effect, datetime.now() + timedelta(seconds=effect['duration'])))
                        self.new_poll = True
                        await asyncio.sleep(45)
                        break
                    except:
                        print('[WARN] Couldn\'t inject. If your game crashed, use !cend, restart game, then !cstart')
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
        if ctx.author.is_mod:
            try:
                os.kill(self.old_pid, 9)
            except PermissionError:
                print('[ERROR] Game is already dead or you don\'t have administrator privileges')
            self.old_pid = None
            self.stopped = True

    @commands.command(name='chaos_help', aliases=['chelp'])
    async def chaos_help(self, ctx):
        await ctx.send('Use !chaos_vote <1-3> or !cvote <1-3> to choose the next effect.')

    @commands.command(name='chaos_vote', aliases=['cvote'])
    async def chaos_vote(self, ctx):
        try:
            vote = int(ctx.message.content.split(' ')[-1])
            if ctx.message.author.name not in self.voted:
                if vote in range(1, 4):
                    self.voted.append(ctx.message.author.name)
                    self.votes[vote] += 1
        except:
            pass

try:
    with open('login.json') as json_file:
        login = json.load(json_file)
    bot = Bot(login)
    bot.run()
except FileNotFoundError:
    print("[ERROR] login.json file was not found")
    input()
