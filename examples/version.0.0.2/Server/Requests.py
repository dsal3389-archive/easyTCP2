from easyTCP2.Server import Server, Group


@Server.Request(name='rooms')
async def show(server, client):
    """
    >>> show
    
    explain:
        showing all the rooms
    """
    await client.send('ROOMS',
        rooms=(
            ['%s %s/%s' %(str(group), len(group.users), group.max_users) for group in Group.groups.values()]
        ) 
    )

@Server.Request()
async def room(server, client, a=None):
    """
    >>> group [-option] [value]

    options:
        a - if you add you can see all the rooms youa are in (debug)

    explain:
        showing your current group
    """
    room=str(client.groups[-1])
    if a is not None:
        room = [str(group) for group in client.groups]
    await client.send('ROOM', ROOM=room)

@Server.Request()
async def say(server, client, m):
    """
    >>> say [-option] [value]

    options:
        m - the message to say to your group
    
    explain:
        sending a message to your group
    """
    if len(client.groups) > 1:
        await client.groups[-1].send(
            'SAY', message=('\tclient %d: %s' %(client.id, m))
        )

@Server.Request()
async def join(server, client, g=''):
    """
    >>> join [-option] [value]

    options:
        g - the room name to join

    explain:
        joining a group
    """
    if not(g in Group.keys()):
        await client.send('ERROR',
            reason='Give group does not exists'
        )
        return

    if len(client.groups) > 1:
        await client.clean_groups()
    await Group[g].add(client)
        
@Server.Request()
async def help(server, client, f='help'):
    """
    >>> help [-option] [value]

    options:
        f - the method name to get help

    explain:
        show a doc (if has) about a method
    """
    if hasattr(server.Request, f):
        await client.send(
            'HELP',
            help=str((getattr(server.Request, f)).__doc__)
        )
