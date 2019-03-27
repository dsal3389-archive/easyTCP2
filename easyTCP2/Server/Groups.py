import asyncio, logging
from ..Exceptions import GroupExceptions

logger = logging.getLogger("Group")


class static_magic(type):
    """
    [:static_magic:]
        this is a metaclass of Group it make
        the group object act like a dict and object in the same time
    
    [:example:]
        Group['clients'] 
        # returns the clients group

        Group.keys()
        # returns the group names
    """
    def __len__(self):
        return len(self.groups)

    def keys(self):
        return self.groups.keys()

    def __getitem__(self, item):
        return self.groups.get(item, None)
        # returns the requested groups if exists if not returnning None

    def __delitem__(self, key):
        group = self.groups[key]
        group.delete()
        # this function is equal to GroupA.delete()


class Group(object, metaclass=static_magic):
    """
    [:Group:]
        to manage permissions and make
        things look clear use Group

    [:params:]
        superusers - if only superusers allowed in in the Group
        name - group name
        max_users(default:100) - how much users allowed in the group
            if you want unlimited users enter None
    """

    groups = {}

    def __init__(self, name, max_users:int=100, superusers:bool=False):
        self.name      = name
        self.for_super = superusers # if the group available from superusers only
        self.max_users = max_users # for unlimited enter None
        self.users     = []
        
        self.__class__.groups[self.name] = self
        logger.info("%s created" %self.name)

    def _check_validation(self, client:object) -> bool:
        """
        [:Group validator:]
            if the group allowing superusers only it checks
            the added user if he is a superuser

        [:params:]
            client - client object to check
        """
        if self.for_super:
            return client.is_superuser
        return True

    @classmethod
    async def get_or_create(cls, name:str) -> object:
        """
        [:Group static func:]
            enter the required name for the group that you are looking for
            if it exists it will return the existing object else it will create it and return it to you
        
        [:params:]
            name - group name
        """groups
        if self.groups.has_key(name):
            return self.group[name]
        return cls(name=name)

    def delete(self) -> None:
        """
        [:Group func:]
            deletes the group object

        [:example:]
            groupa.delete()

            #you can also
            del Group["groupa"]
        """
        del Group.groups[self.name]
        for user in self.users:
            del user.groups[user.groups.index(self)]
        del self

    async def add(self, client:object) -> None:
        """
        [:Group func:]
            adding a given client if you add way more clients base on the given max_users (default:100)
            so this function raise GroupMaxClients from GroupExceptions
        
        [:params:]
            client - the client obj to add
        """
        if self.max_users is not None:
            if (len(self.users) +1) > self.max_users:
                logger.debug("Tried to add too many clients {0}/{0}".format(self.max_users))
                raise GroupExceptions.GroupMaxClients("tried to add more client to %s when there are %d users out of %d" %(self, len(self.users), self.max_users))
        
        permitted = self._check_validation(client)
        if not permitted:
            raise GroupExceptions.UserIsNotSuperuser

        self.users.append(client)
        client.groups.append(self)
        logger.debug("Client via id %d joined %s" %(client.id, str(self)))

    async def remove(self, client:object) -> None:
        """
        [:Group func:]
            removing the given client from the group

        [:params:]
            client - client to remove from the group
        """
        del client.groups[client.groups.index(self)]
        del self.users[self.users.index(client)]
        logger.debug("Client via id %d removed from group %s" %(client.id, str(self)))

    async def send(self, method:str, **kwargs) -> None:
        """
        [:Group func:]
            send a messege in mutli cast to the users in the group

        [:params:]
            method - the method for the send function
            **kwargs - the keyword args to the send function

        [:example:]
            await group1.send("Hello", message="Hello group 1")
        """
        logger.debug("sending multi cast to group %s (method: %s)" %(self.name, method))
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
    