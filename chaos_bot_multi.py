import asyncio
import logging

import socketio
from pymem import Pymem
from pymem.exception import ProcessNotFound

LOGGER: logging.Logger = logging.getLogger("MafiaChaosModTwitch")


async def effect_cooldown(cooldown):
    await asyncio.sleep(int(cooldown))


sio = socketio.AsyncClient()
effect_id = None


@sio.event
async def config(data):
    print(data)
    sleep_task = None
    global effect_id
    duration = data["config"]["duration"]
    cooldown = data["config"]["cooldown"]
    LOGGER.info("Started Chaos Mod")
    LOGGER.warning(f"Go to Vincenzo in the options map and set it to {duration}!")
    try:
        p = Pymem("Game.exe")
    except ProcessNotFound:
        LOGGER.error("Game is not running")
        return
    base = p.process_base.lpBaseOfDll
    pointer = base + 0x2F9464
    while True:
        while not effect_id:  # pyright: ignore[reportPossiblyUnboundVariable]
            await asyncio.sleep(0.25)
        while True:
            await asyncio.sleep(0.25)
            try:
                inGame = p.read_int(base + 0x2F94BC)
                if not inGame:
                    val = p.read_int(pointer)
                    for i in (0x54, 0x688, 0x4, 0x44):
                        val = p.read_int(val + i)  # pyright: ignore[reportOperatorIssue]
                    p.write_float(val + 0x674, effect_id)  # pyright: ignore[reportOperatorIssue]
                    effect_id = None
                    sleep_task = asyncio.create_task(effect_cooldown(cooldown))
                    await asyncio.wait({sleep_task})
                    break
            except Exception as _:
                LOGGER.warning(
                    'Couldn\'t inject. If your game crashed, use !cend, restart game, wait for "Ended Chaos" message, then !cstart'
                )


@sio.event
async def effect(data):
    global effect_id
    effect_id = data["id"]


async def connect_to_server(ip):
    await sio.connect(ip, wait_timeout=100)
    await sio.wait()


if __name__ == "__main__":
    LOGGER.info("You always have to run this as administrator")
    ip = input("Enter server IP: ")
    asyncio.run(connect_to_server("http://" + ip + ":1930"))
