import asyncio, logging

from .Groups import Group
from ..Core  import Protocol
from ..Exceptions      import ServerClientExceptions, GroupExceptions
from ..Core.Decorators import ServerClientDecorators

logger = logging.getLogger("Server Client")


class Client(Protocol, ServerClientDecorators):
    """
    [:Server obj:]
        when recving a new connection the server puts
        the connection reader & writer in this Client object
        so you be able to keep truck and do stuff with the client
        if you want to over write the client object
        make sure you keep the "register" and the "_register" function
        because they used by the server when connection recv

    [:STATICMETHODS:]
        Client.error_codes:
            a dict with numbers as keys and exceptions as value
            if you want to raise error you can call
                raise Client.error_codes[2]("Handshake Error")
            and this will call the
            @Client.error decorator if exists else it raise it uselessliy
    """
    error_codes = {
        2: ServerClientExceptions.HandshakeError,
        6: ServerClientExceptions.Recved404Error,
    } # invis code error is -1 is when recving undefine error code
    _last_client_id = 0

    def __init__(self, reader, writer, server):
        super().__init__(reader, writer, loop=server.loop)
        self.addr         = self.writer.get_extra_info('peername')
        self.id           = self.__class__._last_client_id +1
        self.is_superuser = False
        self.groups = []
        # user related groups

        self.__class__._last_client_id = self.id # updating
        self.server = server

    async def register(self) -> None:
        """
        [:Client func:]
            starting the handshake function
            if the client fail an error will be raised on the decorator
            @Client.error()
        """
        try:
            await asyncio.wait_for(
                self.handshake(),
                20, # timeout
                loop=self.loop
            )
        except Exception: # any exception here is code 2
            await self.raise_error_code(2)
        else:
            await self._register()
            await self.listen()

    async def close(self) -> None:
        """
        [:Client func:]
            this closing the connection with the client but not deleting the object
            so the client object will still exists in groups and other
            and not calling the decorator 
            @Client.left()

        [:example:]
            await client1.close()
        """
        self.writer.close()
    
    async def kill(self) -> None:
        """
        [:Client func:]
            closing the connection and deleting the object
            the client wont appear in groups and wont be useable
            calling decorator
            @Client.left()

        [:example:]
            await client.kill()
        """
        await self.close()
        await asyncio.wait([group.remove(self) for group in self.groups])

        logger.info("Client %d left the server" %self.id)
        self.loop.create_task(self.call('left', server=self.server))

    async def clean_groups(self) -> None:
        """
        [:Client func:]
            removing the client from all the groups
            but keeping the 'client' or the 'superusers' 
            because it not safe to be removed from the build in groups
        """
        for group in self.groups:

            # protected groups to remove from
            if group.name != 'clients' and group.name != 'superusers':
                await group.remove(self)
    
    async def switch_group(self, from_, to):
        """
        [:Client func:]
            switch client group from 1 to 2

        [:params:]
            from_ - the group that the exists in and be removed from
            to - add to group

        [:example:]
            client.groups: # client groups
                ['clients', 'foo']

            await client.switch_group('foo', 'oof')
            # switching

            client.groups:
                ['clients', 'oof']
                # group changed

        """
        if not(from_ in self.groups): 
            raise GroupExceptions.GroupDoesNotExist("cannot switch client to %s when is not exists in %s" %(to, from_))

        if to not in Group.keys():
            raise GroupExceptions.GroupDoesNotExist("not found such group %s" %to)

        await Group[from_].remove(self)
        await Group[to].add(self)
    
    async def handshake(self):
        """
        [:Client method:]
            when a new connection made we need to identify
            the client so we doing it via hanshake
            
            in the default form we can see a very simple handhake

            explaining\example:

                server: {method: 'hanshake'} -> client
                server <- {method: 'handshake'}:client

                server: {method: 'phase1', server_version:'0.0.1'} -> client
                        # client sholud check if the server version is okay

                server <- {method: 'phase1', status: 'okay', version=0.0.1}:client
                        # server checks if he supports client version
        """
        
        # wating to agree for handshake
        await self.send('HANDSHAKE')
        await self.expected('HANDSHAKE')

        # phase 1
        await self.send('PHASE 1', server_version=self.server.version)
        _, code = await self.expected('PHASE 1')

        if not(code['status'].lower() == 'okay') and not(code['version'] in self.server.supported_versions):
            await self.send('BREAK')
            raise ValueError
        await self.send('HANDSHAKE')
    
    async def listen(self):
        """
        [:Client func:]
            when client registerd successfuly
            the server starts to listen for recving data
            and then processing it based on the added requests
        """
        while True:
            try:
                method, data = await self.recv()
            except (ValueError, ConnectionResetError): break
            else:
                self.loop.create_task(self.process(method, data))
                # doing this on a thread so it wont block the next recved data 
        await self.kill()
    
    async def process(self, method:str, data:dict):
        """
        [:Client func:]
            processing the recved message from the connection
            the methods are the function object

        [:params:]
            method - string of the function name
            data - values to pass to the function

        [:example:]
            @Server.Request()
            async def foo(server, client, x):
                print("client given me %s" %x)

            # client.py
            # recving
            # method="foo" and data={"x": "y"}
            process takes and check if foo exists 
            in this case we registered it and now it will pass the data
            to the function
        """
        if len(method)==0: return

        logger.debug("client %d recved (method: %s, data: %s)" %(self.id, method, data))
        if hasattr(self.server.Request, method):
            logger.info("Client with id of %d requested %s" %(self.id, method))
            return await (getattr(self.server.Request, method))(server=self.server, client=self, **data)
        await self.raise_error_code(6) # 404 error
        
    async def raise_error_code(self, code) -> Exception:
        """
        [:Client func:]
            function recv code and based on the error_codes dict
            the function know what error to throw on the decorated function
            via @Client.error

            if no function added with this decorator the function just raise it
            with no meaning

        [:params:]
            code - the code to raise
        """
        error = self.error_codes.get(code, -1)
        # if recving undefine code the invis code -1 will be used

        code = await self.call('error', error=error)
        if code == -1:
            logger.error('Client %d raised %s no "error" decorator added so just rasing it' %(self.id, error))
            raise error

    async def _register(self) -> None:
        """
        [:Client safe:]
            after the client hanshake with no errors we need to tell
            the server to add him to the group and calling the .join decorator
            @Client.join()
        """
        await self.server.add_client(self)

        logger.info("Client %s id:%d registered to the server successfully" %(self.addr, self.id))
        self.loop.create_task(self.call('join'))

    # other __magic__ functions

    def __str__(self):
        return str(self.id)

    def __eq__(self, other):
        return bool(self.id == other)

    def __gt__(self, other):
        return bool(self.id > other)

    def __lt__(self, other):
        return bool(self.id < other)

    def __ge__(self, other):
        return bool(self.id >= other)

    def __le__(self, other):
        return bool(self.id <= other)
