import asyncio
import json
import logging
import random
import sys
from datetime import datetime, timedelta
from math import floor
from typing import TYPE_CHECKING

import asqlite
import psutil
import twitchio
from pymem import Pymem
from pymem.exception import ProcessNotFound
from twitchio import eventsub
from twitchio.ext import commands

from socket_server import send_config, sio, start_socket_server

if TYPE_CHECKING:
    import sqlite3

LOGGER: logging.Logger = logging.getLogger("MafiaChaosModTwitch")


class Bot(commands.AutoBot):
    def __init__(
        self,
        *,
        login,
        shared,
        token_database: asqlite.Pool,
        subs: list[eventsub.SubscriptionPayload],
    ) -> None:
        self.token_database = token_database

        super().__init__(
            client_id=login["CLIENT_ID"],
            client_secret=login["CLIENT_SECRET"],
            bot_id=login["BOT_ID"],
            owner_id=login["CHANNEL_ID"],
            prefix=login["PREFIX"],
            subscriptions=subs,
            force_subscribe=True,
        )

        self.data = {}
        self.blocked = []
        self.queue = []
        self.new_poll = False
        self.stopped = False
        self.broadcaster = login["CHANNEL_ID"]
        self.sleep_task: asyncio.Task | None = None
        self.toggles = ""
        self.duration = 6.0
        self.cooldown = 45
        self.shared = shared
        self.voting = False

    async def setup_hook(self) -> None:
        try:
            with open("effects.json") as json_file:
                self.data = json.load(json_file)
        except FileNotFoundError:
            LOGGER.error("effects.json file was not found")
            input()
            sys.exit(0)

        await self.add_component(BotCommands(self))

    async def event_oauth_authorized(
        self, payload: twitchio.authentication.UserTokenPayload
    ) -> None:
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id:
            return

        subs: list[eventsub.SubscriptionPayload] = [
            eventsub.ChatMessageSubscription(
                broadcaster_user_id=payload.user_id, user_id=self.bot_id
            ),
        ]

        resp: twitchio.MultiSubscribePayload = await self.multi_subscribe(subs)
        if resp.errors:
            LOGGER.warning(
                "Failed to subscribe to: %r, for user: %s", resp.errors, payload.user_id
            )

    async def add_token(
        self, token: str, refresh: str
    ) -> twitchio.authentication.ValidateTokenPayload:
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(
            token, refresh
        )

        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))

        LOGGER.info("Added token to the database for user: %s", resp.user_id)
        return resp

    async def event_ready(self) -> None:
        LOGGER.info("Successfully logged in as: %s", self.bot_id)

    async def event_message(self, payload):
        await self.process_commands(payload)

    async def effect_cooldown(self, cooldown):
        await asyncio.sleep(int(cooldown))


class BotCommands(commands.Component):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command(name="chaos_setup", aliases=["csetup"])
    async def chaos_setup(self, ctx: commands.Context):
        if ctx.author.moderator:  # pyright: ignore[reportAttributeAccessIssue]
            try:
                self.bot.toggles = ""
                p = Pymem("Game.exe")
                base = p.process_base.lpBaseOfDll
                pointer = base + 0x2F9464
                val = p.read_int(pointer)
                for i in (0x54, 0x688, 0x4, 0x44):
                    val = p.read_int(val + i)  # pyright: ignore[reportOperatorIssue]
                reactions = p.read_float(val + 0x658) / 0.7  # pyright: ignore[reportOperatorIssue]
                aggressivity = p.read_float(val + 0x660) / 0.6  # pyright: ignore[reportOperatorIssue]
                intelligence = p.read_float(val + 0x664) / 0.8  # pyright: ignore[reportOperatorIssue]
                sight = p.read_float(val + 0x66C)  # pyright: ignore[reportOperatorIssue]
                for i in (reactions, aggressivity, intelligence, sight):
                    self.bot.toggles += bin(int(round(i)))[2:].zfill(16)[::-1]  # pyright: ignore[reportArgumentType]
                hearing = p.read_float(val + 0x670)  # pyright: ignore[reportOperatorIssue]
                self.bot.cooldown = floor(hearing / 1000)  # pyright: ignore[reportOperatorIssue]
                self.bot.duration = hearing - self.bot.cooldown * 1000 - 100  # pyright: ignore[reportOperatorIssue]
                if self.bot.duration < 0:
                    LOGGER.error(
                        "Chaos mod is disabled in-game, turn it on and run !csetup again"
                    )
                else:
                    LOGGER.info(f"Toggles set to: {self.bot.toggles}")
                    LOGGER.info(f"Cooldown set to: {self.bot.cooldown}")
                    LOGGER.info(f"Base duration set to: {self.bot.duration}")
                send_config(
                    {"duration": self.bot.duration, "cooldown": self.bot.cooldown}
                )
            except ProcessNotFound:
                LOGGER.error("Game is not running")
                return

    @commands.command(name="chaos_start", aliases=["cstart"])
    async def chaos_start(self, ctx: commands.Context):
        if ctx.author.moderator:  # pyright: ignore[reportAttributeAccessIssue]
            self.bot.stopped = False
            await ctx.send("Started Chaos Mod.")
            LOGGER.info("Started Chaos Mod")
            try:
                p = Pymem("Game.exe")
            except ProcessNotFound:
                LOGGER.error("Game is not running")
                return
            base = p.process_base.lpBaseOfDll
            pointer = base + 0x2F9464
            while not self.bot.stopped:
                if not self.bot.queue:
                    effect = self.random_effects(1)[0]
                else:
                    effect = self.bot.queue[0]
                    self.bot.queue.pop(0)
                effect_id = float(effect["id"] * 0.008)
                while not self.bot.stopped:
                    await asyncio.sleep(0.25)
                    try:
                        inGame = p.read_int(base + 0x2F94BC)
                        if not inGame:
                            val = p.read_int(pointer)
                            for i in (0x54, 0x688, 0x4, 0x44):
                                val = p.read_int(val + i)  # pyright: ignore[reportOperatorIssue]
                            p.write_float(val + 0x674, effect_id)  # pyright: ignore[reportOperatorIssue]
                            if self.bot.shared:
                                await sio.emit("effect", {"id": effect_id})
                            self.bot.blocked.append(
                                (
                                    effect,
                                    datetime.now()
                                    + timedelta(
                                        seconds=effect["duration"]
                                        * self.bot.duration
                                        * 15
                                    ),
                                )
                            )
                            self.bot.new_poll = True
                            self.bot.sleep_task = asyncio.create_task(
                                self.bot.effect_cooldown(self.bot.cooldown)
                            )
                            await asyncio.wait({self.bot.sleep_task})
                            break
                    except Exception as _:
                        LOGGER.warning(
                            'Couldn\'t inject. If your game crashed, use !cend, restart game, wait for "Ended Chaos" message, then !cstart'
                        )
            await ctx.send("Ended Chaos.")
            LOGGER.info("Ended Chaos Mod")

    def random_effects(self, count):
        valid_sample = False
        while not valid_sample:
            valid_sample = True
            now = datetime.now()
            sample = random.sample(self.bot.data["effects"], count)
            for i in sample:
                if self.bot.toggles[i["id"] - 1] == "0":
                    valid_sample = False
                    break
                for y in self.bot.blocked:
                    if i["id"] == y[0]["id"]:
                        if now < y[1]:
                            valid_sample = False
                            break
                        else:
                            self.bot.blocked.remove(y)
        return sample  # pyright: ignore[reportPossiblyUnboundVariable]

    @commands.command(name="chaos_poll", aliases=["cpoll"])
    async def chaos_poll(self, ctx: commands.Context):
        if ctx.author.moderator:  # pyright: ignore[reportAttributeAccessIssue]
            self.bot.new_poll = True
            poll = None
            while True:
                await asyncio.sleep(1)
                if self.bot.new_poll:
                    self.bot.new_poll = False
                    sample = self.random_effects(3)
                    self.bot.voting = True
                    if self.bot.user:
                        poll = await self.bot.user.create_poll(
                            title="Vote for the next effect",
                            choices=[s["name"] for s in sample],
                            duration=floor(self.bot.cooldown / 1.5),
                        )
                    await asyncio.sleep(self.bot.cooldown / 1.5)
                    if poll:
                        poll_result = await poll.end_poll(status="ARCHIVED")
                        index = max(
                            range(len(poll_result.choices)),
                            key=lambda i: poll_result.choices[i].votes or 0,
                        )
                        self.bot.queue.append(sample[index])
                    self.bot.voting = False

    @commands.command(name="chaos_end", aliases=["cend"])
    async def chaos_end(self, ctx: commands.Context):
        if ctx.author.name == self.bot.broadcaster.lower():
            self.bot.stopped = True
            try:
                for process in psutil.process_iter():
                    if "Game" in process.name():
                        process.terminate()
            except Exception as _:
                LOGGER.error(
                    "Game is already dead or you don't have administrator privileges"
                )
            try:
                if self.bot.sleep_task:
                    self.bot.sleep_task.cancel()
            except AttributeError:
                LOGGER.warning("Trying to end when not running")

    @commands.command(name="chaos_help", aliases=["chelp"])
    async def chaos_help(self, ctx: commands.Context):
        await ctx.send("Type a number between 1 and 3 to choose the next effect.")


async def setup_database(
    db: asqlite.Pool,
    bot_id,
) -> tuple[list[tuple[str, str]], list[eventsub.SubscriptionPayload]]:
    query = """CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)"""
    async with db.acquire() as connection:
        await connection.execute(query)

        rows: list[sqlite3.Row] = await connection.fetchall("""SELECT * from tokens""")

        tokens: list[tuple[str, str]] = []
        subs: list[eventsub.SubscriptionPayload] = []

        for row in rows:
            tokens.append((row["token"], row["refresh"]))

            subs.extend(
                [
                    eventsub.ChatMessageSubscription(
                        broadcaster_user_id=row["user_id"], user_id=bot_id
                    )
                ]
            )

    return tokens, subs


def create_login():
    login = {}
    login["BOT_ID"] = input(
        "Enter your Twitch bot ID (https://streamscharts.com/tools/convert-username): "
    )
    login["CHANNEL_ID"] = input(
        "Enter your Channel ID (https://streamscharts.com/tools/convert-username): "
    )
    login["PREFIX"] = input("Enter your command prefix (!, $, ., etc.): ")
    LOGGER.info(
        "Go to https://dev.twitch.tv/console and Register Your Application (Category must be Chat Bot, Redirect URLs must be http://localhost)"
    )
    login["CLIENT_ID"] = input("Paste Client ID: ")
    login["CLIENT_SECRET"] = input("Paste Client Secret: ")
    with open("login.json", "w") as json_file:
        json.dump(login, json_file)


def main() -> None:
    twitchio.utils.setup_logging(level=logging.INFO)

    async def runner(login, shared) -> None:
        async with asqlite.create_pool("tokens.db") as tdb:
            tokens, subs = await setup_database(tdb, login["BOT_ID"])

            if shared:
                asyncio.create_task(start_socket_server())

            async with Bot(
                login=login, shared=shared, token_database=tdb, subs=subs
            ) as bot:
                for pair in tokens:
                    await bot.add_token(*pair)

                await bot.start(load_tokens=False)

    try:
        try:
            with open("login.json") as json_file:
                login = json.load(json_file)
        except FileNotFoundError:
            LOGGER.error("login.json file was not found")
            create_login()
            input("Done. Relaunch the bot.")
            sys.exit(0)

        LOGGER.info(
            "If your bot doesn't work, delete login.json file and start this program again"
        )
        LOGGER.info("You always have to run this as administrator")
        shared_effects = input("Do you want to share your effects? (y/n) ")
        if shared_effects.lower() == "y":
            shared = True
        else:
            shared = False

        asyncio.run(runner(login, shared))
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt")


if __name__ == "__main__":
    main()
