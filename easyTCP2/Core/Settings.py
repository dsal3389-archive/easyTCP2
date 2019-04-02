import json



class Settings(object):
    server = {}
    client = {}
    protocol   = {}
    encryption = {}

    @staticmethod
    def set_encryption(settings:dict) -> None:
        """
        [:Settings static func:]
            if you want to add encryption to your server is the best
            to do it in your way so in the settings just drop the object here
            and make sure you have "dencrypt" and "encrypt" functions in your object

        [:NOTE:]
            you must add to your object "encrypt" and "dencrypt" functions
            the "dencrypt" function:
                1. must recv 1 parameter (the encrypted data)
                2. must return the string

            the "encrypt" function:
                1. must recv 1 paramter (recv data as bytes to encrypt)
                2. must return bytes

            for example check:
                https://github.com/dsal3389/easyTCP/blob/master/easyTCP/SERVER/utils/DEFAULT_ENCRYPTION.py
                (from easyTCP first version)

        [:example:]
            Settings.use_default()
            Settings.set_encryption({
                'object': Encrypt(...)
            })
        """
        Settings.encryption = {**Settings.encryption, **settings}

    @staticmethod
    def set_protocol(settings:dict) -> None:
        """
        [:Setting static func:]
            the protocol is a shared object between client and server
            that mean if you want your server to read 4096 bytes change the read size
            but in the same time it changing the client (in easyTCP2.Client.Client) read size
        
        [:example:]
            Settings.use_default()
            Settings.set_protocol({
                'read_size': 2048,
            })
        """
        Settings.protocol = {**Settings.protocol, **setttings}

    @staticmethod
    def set_server(settings:dict) -> None:
        """
        [:Settings static func:]
            changing\setting the given settings to the server settings
        
        [:NOTE:]
            I recommand using first the user_default() function and then
            this function
        
        [:example:]
            Settings.use_default()
            Settings.set_server({
                'ip': '0.0.0.0',
                'client':{
                    'read_size': 2048
                }
            })
        """
        Settings.server = {**Settings.server, **settings}

    @staticmethod
    def set_client(settings:dict) -> None:
        """
        [:Settings static func:]
            changing\setting the given settings to the client settings
        
        [:NOTE:]
            I recommand using first the user_default() function and then
            this function
        
        [:example:]
            Settings.use_default()
            Settings.set_client({
                'ip': '0.0.0.0',
                'client':{
                    'read_size': 2048
                }
            })
        """
        Settings.client= {**Settings.client, **settings}

    @staticmethod
    def use_default() -> None:
        """
        [:Settings static func:]
            setting default settings for server && client
        
        [:NOTE:]
            I recommand to use this function first and then make
            changes to the settings

        [:example:]
            Settings.use_default()
        """

        Settings.protocol={
            'read_size': 4096,
            'encoding': 'utf-8',
            'timeout': 30 # in seconds
        }

        Settings.server={
            'ip': '127.0.0.1',
            'port': 25569,
            'client':{
                'obj': 'easyTCP2.Server.Client.Client'
            }
        }

        Settings.client={
            'ip': '127.0.0.1',
            'port': 25569,
        }

        Settings.encryption={
            'object': None,    
        }

