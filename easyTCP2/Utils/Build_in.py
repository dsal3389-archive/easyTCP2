from ..Server import Server


@Server.Request()
async def help(server, client, f):
    """
    [:BUILD IN:]
        when import this file you recv some requests
        that I have build to make it easy for you or just an example
    
    [:NOTE:]
        I recommand to change BUILD_IN function __doc__
        because if you use that build in help method
        it returns the function __doc__

    [:example:]
        from easyTCP2.Utils.Build_in import *
    """
    if f in server.requests.keys():
        return (await client.send("help", server.requests[f].__doc__))
    return (await client.send(2, reason='unknown method %s' %f))

