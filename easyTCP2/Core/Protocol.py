import asyncio, json, logging
from ..Core.Settings import Settings

logger = logging.getLogger('\teasyTCP | protocol')


def json_dumper(data:dict):
    """
    [:Protocol util:]
        converts a dict to json string and then to bytes
        via json package to be able to send it on the connection
    
    [:params:]
        data - dict to convert
    """
    data = json.dumps(data)
    return bytes(data, encoding=Settings.protocol['encoding'])

def json_loader(data:bytes):
    """
    [:Protocol util:]
        converts the recved data from bytes to string and then
        to python dict

    [:params:]
        data - bytes to convert to dict
    """
    return json.loads(str(data, encoding=Settings.protocol['encoding']))


class Protocol(object):
    """
    [:Protocol core:]
        the clients and the server using the same logic to
        send and recv data so them both implementing from this class

    [:params:]
        reader - client reader
        writer - client writer
        loop(optional) - event loop
    """
    def __init__(self, reader=None, writer=None, *, loop=None):
        self.reader = reader
        self.writer = writer

        self.loop  = loop or asyncio.get_event_loop()

        self.to_python = json_loader
        self.to_bytes = json_dumper

    async def send(self, method:str, *, drain:bool=False, **kwargs) -> None:
        """
        [:core:]
            send data to the client via given encoding in settings

        [:params:]
            method - the method name
            **kwargs - data

        [:example:]
            await client1.send('handshake', data="some data", id=client1.id, foo=True)
        """
        data = self.to_bytes({'method':method, **kwargs})
        self.writer.write(data)

        if drain:
            await self.writer.drain()

    async def recv(self) -> tuple:
        """
        [:core:]
            recv data from the client and returning a tuple that contain method and data

        [:example:]
            method, data = await client1.recv()
        """
        data = await self.reader.read(Settings.protocol['read_size'])
        data = self.to_python(data)

        return data['method'], {k:i for k, i in data.items() if k != 'method'}

    async def expected(self, *args) -> tuple:
        """
        [:core:]
            enter expected methods if recv unexpected method ValueError will be raised

        [:params:]
            *args - expected methods

        [:example:]
            method, data = await client1.expected('hello', 'no')
        """
        method, _ = await self.recv()
        if args and method not in method:
            raise ValueError('expected %s recved %s' %(args, method))
        return method, _

    def __await__(self):
        return self.recv().__await__()