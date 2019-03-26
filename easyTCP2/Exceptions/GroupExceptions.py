

class GroupMaxClients(Exception):
    """tried to add to many users to a group"""

class GroupDoesNotExist(Exception):
    """the requested group does not exists"""
