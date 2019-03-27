import asyncio, logging
from .Groups import Group
from ..Core.Decorators import ServerDecorators
from ..Core.Settings import Settings

logger = logging.getLogger("Server")


class Server(ServerDecorators):
    """
    [:server obj:]
        the server main object

    [:params:]
        ip - the ip the server is gonna run on
        port - the port the server is gonna run on
        loop(optional) - the asyncio event loop

    [:STATICMETHODS:]
        Server.supported_versions:
            the supported client versions (used by handshake function in the client object)

        Server.groups:
            grop of client via permissions (easyTCP2.Core.Groups <- the object)

        Server.events:
            added event via @Server.Event decorator
            this is a dict so you be able to access your event easyly via
            event name and cancle or else
        
        Server.Client:
            the object that every new connection gonna be appended to

        Server.Requests:
            all added requests via Server.Request() decorator added
            as a staticmethod the the Request object
    """
    events   = {}
    threads  = []
    supported_versions = ['0.0.1'] # used by the handshak function in Client object
    # enter the supported client versions here

    _running_server_object = None

    def __init__(self, ip=None, port=None, *, loop=None):
        self.ip     = ip   or Settings.server['ip']
        self.port   = port or Settings.server['port']
        self.client = Server._get_client(Settings.server['client']['obj'])

        self.loop    = loop or asyncio.get_event_loop()
        self.version = '0.0.1' # change this

    @classmethod
    def get_current(cls) -> object or None:
        """
        [:server static func:]
            returnning the running server object

        [:NOTE:]
            this is useful when you have @Server.Event() and you want
            access to the current server object
        """
        return cls._running_server_object

    async def run(self):
        """
        [:server func:]
            when called the server starts to run on the given port & IP
            you can do this also by awating the server obj
        """
        self.connection = await asyncio.start_server(
            self.handle_connection,
            self.ip, self.port
        )
        await self._setup()

    async def _setup(self):
        """
        [:server safe func:]
            all the things the server need to do when connected
        """
        logger.info("server started running (ip: %s| port: %d)" %(self.ip, self.port))
        
        Group('clients', None),
        Group('superusers', None)
        
        self.__class__._running_server_object = self
        asyncio.ensure_future(self._event_listener(), loop=self.loop)
        self.loop.create_task(self.call('ready'))

    async def handle_connection(self, reader, writer):
        """
        [:server func:]
            when recving a new connection we append it to a client obj
            and starting the registeration

        [:params:]
            reader - connection reader
            writer - connection writer
        """
        client = self.client(reader=reader, writer=writer, server=self)
        asyncio.ensure_future(client.register(), loop=self.loop)

    async def add_client(self, client) -> None:
        """
        [:server func:]
            when client register successfuly he is added to a group
            if client is a superusers he will be added to the superuser group and else

        [:params:]
            client - client to add to the build in groups
        """
        if client.is_superuser:
            await Group.groups['superusers'].add(client)
        else:
            await Group.groups['clients'].add(client)

    async def remove_client(self, client) -> None:
        """
        [:server func:]
            removing the given client

        [:params:]
            client - the client obj to remove
        """
        await client.kill()
        del client
    
    async def _event_listener(self) -> None:
        """
        [:server func:]
            this function is running on a thread in case
            you add a lot of event so the server wont lose 
            of his speed
            (if there are no event the server return and wont use the thread)
        
        [:NOTE:]
            events are those functions you add with the decorator
            @Server.Event(3)
        """
        logger.debug("Starting events, events registered %d" %len(self.events))
        if len(self.events) == 0: return
        # break this thread because there are no events

        [self.loop.create_task(event.start()) for event in self.events.values()]

    def __str__(self):
        """
        [:server magic:]
            retruns the ip of the server
        """
        return self.ip

    def __await__(self):
        """
        [:server magic:]
            running the server on the give port & IP 
            can be done via .run()
        """
        return self.run().__await__()

    @staticmethod
    def _get_client(import_path) -> object:
        """
        [:server static safe:]
            this function importing and returning
            the given object in the Settings
        
        [:params:]
            import_path - the.path.to.the.object
        """
        if not(isinstance(import_path, str)): # mean that you gave the object itself
            return import_path
        
        ls_import_path = import_path.split('.')
        if len(ls_import_path) <= 1:
            raise ImportError("given import is not importing object but the path to the import")
        globals()['Client'] = __import__("{}".format('.'.join(ls_import_path[0:-1])), fromlist=[ls_import_path[-1]])
        # adding the local import to the global variables as Client

        return Client.Client


