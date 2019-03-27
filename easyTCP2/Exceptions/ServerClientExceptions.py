

class HandshakeError(Exception):
    """could not handshake with the other end (code: 2)"""

class Recved404Error(Exception):
    """current future got 404 response (code: 6)"""

class ClientDoesNotHasAccess(Exception):
    """client does not have access to the requested method"""

class ConnectionClosedWithClient(Exception):
    """client closed the connection with server"""

