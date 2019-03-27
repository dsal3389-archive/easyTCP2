import asyncio, logging
from easyTCP2.Core.Settings import Settings
from easyTCP2.Server import Server, Client, Group
from easyTCP2 import Utils

logging.basicConfig(filename='server.log', level=20, format=Utils.logger_format)

extend_modules = ['Events', 'Requests']
Settings.use_default()

#for file in extend_modules:
#    Utils.load_external_module(file)


@Server.ready()
async def ready(server):
    print('[ready] server is ready on ip: %s and port: %d' %(server.ip, server.port))

    # creating groups
    Group('room1', 20)
    Group('room2', 20)
    Group('room3', 20)


@Client.join()
async def cjoin(client):
    print("[join] client %d joined" %client.id)

@Client.left()
async def cleft(client, server):
    print("Client %d left the server" %client.id)


async def main(loop):
    server = Server(loop=loop)
    await server


if __name__=="__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

    try:
        loop.run_forever()
    finally:
        loop.close()
