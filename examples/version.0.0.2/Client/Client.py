import asyncio, sys, logging

sys.path.append('..')

from easyTCP2 import Utils
from easyTCP2.Client import Client
from easyTCP2.Core.Settings import Settings

Settings.use_default()
logging.basicConfig(
    filename='Client.log', 
    level=20, 
    format=Utils.logger_format
)

@Client.ready()
async def foo(client):
    print('Client connected to server (ip: %s, port: %s)' %(client.ip, client.port))

@Client.leave()
async def oof(client):
    print('Client left the server')

@Client.on_recv()
async def recver(client, method, data):
    print("\n\nMETHOD: " +method)
    for k, v in data.items():
        print(k +":")
        
        if isinstance(v, str):
            print(v)
        
        elif isinstance(v, list):
            for i in v:
                print("\t", i)
        else:
            print(v)



async def main(loop):
    client = Client(ip='127.0.0.1', port=25569, loop=loop)
    await client.connect()

    while True:
        c = await loop.run_in_executor(None, input, '>>> ')

        to_send = await Utils.string_to_dict(c)
        await client.send(**to_send)


if __name__=="__main__":
    loop=asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

    try:
        loop.run_forever()
    finally:
        loop.close()