import asyncio
from ..Exceptions import GroupExceptions


class Group(object):
    """
    [:Group:]
        to manage permissions and make
        things look clear use Group

    [:params:]
        name - group name
        max_users(default:100) - how much users allowed in the group
            if you want unlimited users enter None
    """
    def __init__(self, name, max_users=100):
        self.name      = name
        self.max_users = max_users # for unlimited enter None
        self.users     = []

    async def add(self, client) -> None:
        """
        [:Group func:]
            adding a given client if you add way more clients base on the given max_users (default:100)
            so this function raise GroupMaxClients from GroupExceptions
        
        [:params:]
            client - the client obj to add
        """
        if self.max_users is not None:
            if (len(self.users) +1) > self.max_users:
                raise GroupExceptions.GroupMaxClients("tried to add more client to %s when there are %d users out of %d" %(self, len(self.users), self.max_users))
        self.users.append(client)
        client.groups.append(self)

    async def remove(self, client) -> None:
        """
        [:Group func:]
            removing the given client from the group

        [:params:]
            client - client to remove from the group
        """
        del client.groups[client.groups.index(self)]
        del self.users[self.users.index(client)]

    async def send(self, method, **kwargs) -> None:
        """
        [:Group func:]
            send a messege in mutli cast to the users in the group

        [:params:]
            method - the method for the send function
            **kwargs - the keyword args to the send function

        [:example:]
            await group1.send("Hello", message="Hello group 1")
        """
        if not(len(self.users)):
            return # if the len = 0 its False but the "not" makes it True so 
                   # there is no need to send messages to none
        await asyncio.wait([user.send(method, **kwargs) for user in self.users])

    async def superusers(self) -> tuple:
        """
        [:Generator:]
            a generator that returns all of the superusers objects in the group
        """
        for user in self.users:
            if user.is_superuser:
                yield user

    async def search(self, **kwargs) -> tuple:
        """
        [:Generator:]
            search for a user in the group based on the given params

        [:NOTE:]
            the given pramas should exists in the users object
            
        [:example:]
            usr = await groupA.search(id=3, is_superuser=True)
        """
        for user in self.users:
            search_params = len(kwargs)
            found_true = 0

            for k, v in kwargs.items():
                if getattr(user, k) == v:
                    found_true += 1
            if search_params == found_true:
                yield user
    
    def __str__(self):
        return self.name

