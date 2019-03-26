import asyncio
from ..Core import Protocol
from ..Core.Decorators import ClientDecorators


class Client(Protocol, ClientDecorators):
    version = '0.0.1'
    supported_versions = ['0.0.1']

    def __init__(self, ip, port, *, loop=None):
        super().__init__(loop=loop)
        self.ip = ip
        self.port = port

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.ip, self.port, loop=self.loop
        )
        self.loop.create_task(self.register())

    async def register(self):
        try:
            await asyncio.wait_for(
                self.handshake(), 20, loop=self.loop
            )
        except Exception as e:
            #await self.raise_error_code
            raise e
        else:
            await self.run()

    async def handshake(self):

        # wating to agree for handshake
        await self.expected('HANDSHAKE')
        await self.send('HANDSHAKE')
    
        # phase 1
        status = 'not okay'
        _, version = await self.expected('PHASE 1')
        if version['server_version'] in self.supported_versions:
            status = 'okay'

        await self.send('PHASE 1', status=status, version=self.version)
        await self.expected('HANDSHAKE')

    async def run(self):
        asyncio.ensure_future(self.listen(), loop=self.loop)
        await self.call('ready')

    async def listen(self):
        while True:
            try:
                method, data = await self.recv()
            except: break
            else:
                asyncio.ensure_future(self.process(method=method, data=data), loop=self.loop)
    
    async def process(self, method, data, *args, **kwargs):
        print(method)
        print(data)


