import asyncio, logging
from easyTCP2.Utils import logger_format
from easyTCP2.Core.Settings import Settings
from easyTCP2.Server import Server, Client

logger = logging.basicConfig(
    format=logger_format, 
    filename='Server.log', 
    level=20
)


@Server.ready()
async def ready(server):
    print("Server running (ip: %s | port: %d)" %(server.ip, server.port))

@Client.join()
async def cjoin(client, server):
    print('[JOIN] client joined (id: %d)' %client.id)

@Client.left()
async def cleft(client, server):
    print('[LEFT] client left the server (id: %d)' %client.id)


async def main(loop):
    Settings.use_default()

    server=Server(loop=loop)
    await server

if __name__=="__main__":
    loop=asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

    try:
        loop.run_forever()
    finally:
        loop.close()

