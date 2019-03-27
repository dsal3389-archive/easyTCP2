from easyTCP2.Server import Server, Group


@Server.Event(60) # event 60s
async def hello_world():
    print('Hello world im an event!')



