import asyncio, logging
from ..Exceptions import ClientExceptions

logger = logging.getLogger("Decorator")


class BASE_DECORATOR(object):
    def __init__(self, parent:object, *args, **kwargs):
        self.parent = parent
        self.args   = args
        self.kwargs = kwargs

    def __call__(self, func):
        self.func = func
        if self.validate():
            setattr(self.parent, str(self), func)
            logger.info("%s created on parent(server) is on %s" %(self, self.parent))
        else:
            logger.warning("%s is not valid so it hasn't added!" %self)

    def validate(self) -> bool:
        """
        [:validator:]
            checks that the given function is coroutine
        """
        return asyncio.iscoroutinefunction(self.func)

    def __str__(self):
        return self.__class__.__name__


class DecoratorUtils:
    async def call(self, name:str, *args, **kwargs) -> None:
        """
        [:Decorator util:]
            the correct way to call decorated functions (not Requests)

        [:params:]
            name - decorator name like ('ready', 'close', etc...)
            *args - parse args to the function
            **kwargs - parse keyword arguments to the function
        """
        logger.debug("Calling decorated function %s" %name)
        if hasattr(self, name):
            f = getattr(self, name)
            if self.is_okay_function(f):
                return (await f(*args, **kwargs))

        logger.warning("Failed calling %s" %name)
        return -1 # means there is no such decorated function

    def is_okay_function(self, func) -> bool:
        """
        [:Decorator util:]
            called by the call util function to valid the function

        [:params:]
            func - function to valid
        """
        try:
            return asyncio.iscoroutinefunction(func)
        except: return False # may raise error because most of the time
        # the parameter is a class and the "iscoroutinefunction" checks for functions only


class ServerDecorators(DecoratorUtils):
    """
    [:decorator(s):]
        server decorators that you can access with the server object
        do not import this file and start using it!!

    [:to recv params:]
        server - the running server object

    [:example:]
        @Server.ready()
        async def foo(server):
            print("Server is ready and running on (ip %s | port %d)" %(server.ip, server.port))

    [:NOTE:]
        do not import this file and start using in it wont work
        the server object is a subclass of this class
        and make sure your mathod gets a server as the first parameter
    """

    @classmethod
    class ready(BASE_DECORATOR):
        """
        [:decorated:]
            called when servers is started running

        [:params:]
            server - server object
        """

    @classmethod
    class Event(BASE_DECORATOR):
        """
        [:decorator:]
            if you want a function to appear every x time
            use event decorator

        [:to recv params:]
            *args/**kwargs - all you enter in **kwargs and *args 
                should be recved in your function event

        [:params:]
            timer - when to appear after given time
            *args - args to parse to your event
            **kwargs - keyword args to parse to your event

        [:example:]
            @Server.Event(3, name="Daniel")
            async def foo(name):
                print("got name %s" %name)
        """
        def __init__(self, parent:object, timer:int, *args, **kwargs):
            super().__init__(parent, *args, **kwargs)
            self.timer = self.Timer(timer, *self.args, **self.kwargs)

            self.loop   = asyncio.get_event_loop()
            self.future = None
            self._create_future()
            # just getting the running event and creating future

            logger.info('Event %s created' )

        def _create_and_run(self, *args, **kwargs):
            """
            [:Event func safe:]
                creates a future and run it after
                this called when first created future finished and needs to create himself again
            """
            _ = self._create_future()
            if _ == 0: return

            self.loop.create_task(self.start())

        def _create_future(self, *args, **kwargs):
            """
            [:Event func safe:]
                this creates a new future and adds him a callback
                and updating the Timer future
            """
            if self.future is not None:
                if self.future.cancelled(): # if you cancelled it wont come back
                    logger.info("%s cancelled aborting..." %self.timer)
                    return 0
                
            self.future = self.loop.create_future()
            self.future.add_done_callback(self._create_and_run)
            self.timer.future = self.future
            # the future refreshing himself

            logger.debug("%s created future for the Event via callback" %self)
        
        def __call__(self, func):
            self.func = func
            if self.validate():
                self.timer.func = self.func
                self.parent.events[str(self)] = self
        
        async def start(self):
            await self

        def __await__(self): # awating the appended event starting it
            return self.timer.start().__await__()

        def __str__(self):
            return 'undefine' if not(hasattr(self, 'func')) else self.func.__name__
        
        class Timer(object):
            """
            [:Event obj safe:] (!not to use directliy!)
                this is sort of proxy to await for the given time
                and activate the function after awaited
        
            [:params:]
                time - timer
                *args - args to parse to the function
                **kwargs - keyword args to parse to the function
            """
            def __init__(self, time:int, *args, **kwargs):
                self.time   = time 
                self.future = None # added manually
                self.args   = args
                self.kwargs = kwargs
            
            async def start(self):
                """
                [:Timer func:]
                    starting the sleep time and when finished 
                    returnning the requested function
                """
                await asyncio.sleep(self.time)
                await self.func(*self.args, **self.kwargs)
                self.future.set_result(1)
                logger.debug("Event %s finished after waitng %ds" %(self.func.__name__, self.time))
        
    @classmethod
    class Request(object):
        """
        [:decorator:]
            to add methods for your server use this decorator every added function appended to the server as a Func object
            make sure your function get server and client as paramters

        [:to recv params:]
            server - the running server object
            client - client who requested the added request
            custom - get what you want to get for this function
                look at the second example 
        
        [:params:]
            superuser(default:False) - if True the request be allowed only for superusers
            allowed_groups(default:['*']) - list of group names the '*' mean everyone, only the client in the group will be allowed to use the request

        [:example:]
            1.================================
            @Server.Request()
            async def foo(server, client):
                print("method foo called from %d" %client.id)

            2.================================
            if you want the function to get parameters the client need to enter them
            just add this normaly

            @Server.Request()
            async def foo(server, client, foo, oof=False):
                print("foo called (foo=%s, oof=%s)" %(foo, oof))


            2.1================================
            catch you requests error use

            @Server.Request.foo.error
            async def oof(foo, client, error):
                print("my %s method raised %s" %(foo, error))
            # the foo parameter is the Func object of the current function
        """
        def __init__(self, parent:object, *, name=None, superuser:bool=False, allowed_groups:list=['*']):
            self.server    = parent
            self.name      = name
            self.for_super = superuser
            self.allowed_groups = allowed_groups
            # this request be allowed to users in the given group name
        
        def __call__(self, func):
            self.func = self.Func(
                name=self.name,
                func=func, 
                superusers=self.for_super, 
                allowed_groups=self.allowed_groups
            )
            if self.func.valid():
                setattr(self.__class__, str(self.func), self.func)
                logger.info("%s added to the parent(server) object" %self.func)
            else:
                logger.warning("Failed adding %s to the parent(server)" %self.func)
                    
        @classmethod
        async def remove(cls, func_name:str) -> None:
            """
            [:Request classmethod func:]
                deletes the given function name

            [:params:]
                func_name - function name to delete

            [:example:]
                await Server.Request.remove('foo')
            """
            if hasattr(cls, func_name):
                delattr(cls, func_name)
                logger.warning("Request %s deleted from the parent(server)" %func_name)

        class Func(object):
            """
            [:Request obj:]
                for every added request the Request decorator build a new
                class from here to check validation everytime and more

            [:params:]
                name - request custome name (if none given the decorated function will be the name)
                func - the added func as request
                superusers - parsed from the Request object
                allowed_groups - parsed from the Request object
            """
            def __init__(self, name, func, superusers:bool, allowed_groups:list):
                self.func      = func
                self.for_super = superusers
                self.allowed_groups = allowed_groups
                self.name   = self.get_name(name)

                self.server = None
                self.client = None

                self.args   = ()
                self.kwargs = {}

            @property
            def __doc__(self):
                return self.func.__doc__

            def get_name(self, name):
                """
                [:validator/func:]
                    getting the given name if None (as default) the request
                    name will be the decorated function name

                [:param:]
                    name - passed name to the Request decorator
                """
                if name == None:
                    return self.func.__name__ 
                ls = name.split(' ')
                return '_'.join(ls) # removing the spaces

            def valid(self):
                return asyncio.iscoroutinefunction(self.func)

            def check_permissions(self, client:object) -> bool:
                """
                [:validator:]
                    checks if the function caller has access to call this function
                
                [:params:]
                    client - client to check if he has access
                """
                if client.is_superuser: return True
                # superusers have access to everything in the server      
                
                if "*" not in self.allowed_groups:
                    return any(str(group) in self.allowed_groups for group in client.groups)
                    
                if self.for_super: return client.is_superuser 

                return True

            def __call__(self, server:object, client:object, **kwargs):
                self.server = server
                self.client = client
                self.kwargs = kwargs

                client_has_access = self.check_permissions(self.client)
                if client_has_access:
                    return self
                
                logger.warning("Client %s id: %d tried to use method with no permissions to use it" %(client.addr, client.id))
                return (self._call_error())(server=self.server, client=self.client, error=ClientExceptions.ClientDoesNotHasAccess)
            
            def __await__(self):
                return self.func(
                    server=self.server, 
                    client=self.client,
                    *self.args, **self.kwargs
                ).__await__()

            def __str__(self):
                return self.name
            
            def _call_error(self):
                """
                [:Request Func func:]
                    checks if error_fetcher added
                    (error_fetcher - added via @Server.Request.foo.error)
                """
                if hasattr(self, 'error_fetcher'):
                    return getattr(self, 'error_fetcher')
                logger.warning('%s tried to call the error_fetcher but not found any' %self)
                return lambda: None

            @classmethod
            def error(cls, func):
                """
                [:decorator:]
                    add this to catch your request method error
                
                [:NOTE:]
                    make sure your error fetcher recv the next parameters

                [:to recv params:]
                    error - this is the error that your method raised
                    client - client who requested the and probobly raised it
                    server - server object that this function is running on
                
                [:example:]
                    @Server.Request(superusers=True)
                    async def foo(server, client):
                        print("something")

                    @Server.Request.foo.error
                    async def oof(foo, client, error):
                        if isinstance(ClientExceptions.ClientDoesNotHasAccess, error):
                            print("%d tried to access %s with no permissions" %(client.id, foo))
                """
                if asyncio.iscoroutinefunction(func):
                    logger.debug("Added error_fetcher to \"%s\"" %func.__name__)
                    return setattr(cls, 'error_fetcher', func)
                    
                logger.error("Added error_fetcher (%s) is not coroutine raised ValueError" %func.__name__)
                raise ValueError("%s is not coroutine function for the error_fetcher" %func.__name__)


class ServerClientDecorators(DecoratorUtils):

    @classmethod
    class join(BASE_DECORATOR):
        """
        [:decorator:]
            called when a new connection made and register successfuly
        
        [:params:]
            client - the registerd client
        """

    @classmethod
    class left(BASE_DECORATOR):
        """
        [:decorator:]
            called when client leaving the session
            or when client.kill() is called (not client.close())
        
        [:params:]
            client - the client who left/killed
            server - server object
        """

    @classmethod
    class error(BASE_DECORATOR):
        """
        [:decorator:]
            called when client raise error

        [:params:]
            client - the client who raised the error
            error  - the error that was raised 
        """


class ClientDecorators(DecoratorUtils):
    
    @classmethod
    class ready(BASE_DECORATOR):
        """
        [:decorator:]
            called when client registered to server

        [:params:]
            client - your client object
        """

    @classmethod
    class leave(BASE_DECORATOR):
        """
        [:decorator:]
            called when client leaving/connection closed

        [:params:]
            client - your client object
        """

    @classmethod
    class error(BASE_DECORATOR):
        """
        [:decorator:]
            when client rasing error you can catch it
            with this decorator

        [:params:]
            client - your client object
            error - the error
        """
    
    @classmethod
    class on_recv(BASE_DECORATOR):
        """
        [:decorator:]
            when client recving data it passed to
            the default process function and move from there
            if you use this decorator you will overwrite the default
            process function and your function will be the new "processor"

        [:params:]
            client - your client object
            method - recved method as a string
            data - data as a dict

        [:example:]
            @Client.on_recv()
            async def recving(client, method, data):
                print("method:%s\ndata:\n\t %s" %(method, data))
        """
