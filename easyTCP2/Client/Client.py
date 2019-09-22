import asyncio, logging
from ..Core import Protocol
from ..Core.Decorators import ClientDecorators
from ..Exceptions import ClientExceptions

logger = logging.getLogger("Client")

class Client(Protocol, ClientDecorators):
    """
    [:Client obj:]
        async client to connection to your server

    [:params:]
        ip - servers ip
        port - server port
        loop(optional) - running event loop

    [:STATICMETHODS:]
        Client.version:
            the client version, in the defaukt handshake process
            the server checks the client version and see if he supports it

        Client.supported_version:
            the server versions that the client supports

        Client.error_codes:
            the keys are numbers (code) and the value its the Exception
    """
    version = '0.0.1'
    supported_versions = ['0.0.1']

    error_codes = {
        2: ClientExceptions.HandshakeFaileException
    }

    def __init__(self, ip:str, port:int, *, loop=None):
        super().__init__(loop=loop)
        self.ip = ip
        self.port = port

    async def connect(self):
        """
        [:Client func:]
            stating the connection with the server after
            connecting starting the resgister process
        """
        self.reader, self.writer = await asyncio.open_connection(
            self.ip, self.port, loop=self.loop
        )
        self.loop.create_task(self.register())

    async def register(self) -> None:
        """
        [:Client func:]
            start registering to the server
        """
        try:
            await asyncio.wait_for(
                self.handshake(), 20, loop=self.loop
            )
        except Exception as e:
            await self.raise_error_code(2)
        else:
            await self.run()

    async def raise_error_code(self, code:int) -> None or Exception:
        """
        [:Client func:]
            rasing Exception based on the given code
        
        [:params:]
            code - rasing it base on Client.erro_codes
        """
        error = self.error_codes.get(code, -1)
        # if recving undefine code the invis code -1 will be used

        code = await self.call('error', error=error)
        if code == -1:
            logger.error('Client %d raised %s no "error" decorator added so just rasing it' %(self.id, error))
            raise error

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
        """
        [:Client func:]
            when client registered he is starting to
            listen to the server
        """
        asyncio.ensure_future(self.listen(), loop=self.loop)
        await self.call('ready')

    async def listen(self) -> None:
        """
        [:Client func:]
            listening to the server connection and sending the data
            to the _processor that decide where it is going
        """
        while True:
            try:
                method, data = await self.recv()
            except: break
            else:
                asyncio.ensure_future(self._process(method=method, data=data), loop=self.loop)
        await self.kill()

    async def kill(self) -> None:
        """
        [:Client func:]
            closing connection with server
            and calling @Client.leave()
        """
        self.writer.close()
        await self.call('leave')

    async def _process(self, method:str, data:dict):
        """
        [:Client safe func:]
            checks if the on_recv decorator exsits
            and send the recv data to him else using the default processor

        [:params:]
            method - recv data
            data - recv data keyword arg
        """
        okay = await self.call('on_recv', method=method, data=data)

        if okay == -1:
            await self.process(method=method, data=data)
    
    async def process(self, method:str, data:dict): # not ready
        pass


