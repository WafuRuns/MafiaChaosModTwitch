import logging

import socketio
from aiohttp import web

LOGGER: logging.Logger = logging.getLogger("MafiaChaosModTwitch")
config = {}

sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
app = web.Application()
sio.attach(app)


@sio.event
async def connect(sid, environ):
    LOGGER.info(f"Client connected: {sid}")
    await sio.emit("config", {"config": config}, to=sid)


def send_config(new_config):
    global config
    config = new_config


async def start_socket_server(host="0.0.0.0", port=1930):
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    LOGGER.info(f"Sharing server running at http://{host}:{port}")
