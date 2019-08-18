def escape_ResourceWarning(sock):
    # excape WARNING
    # ResourceWarning: Enable tracemalloc to get the object allocation traceback
    # ResourceWarning: unclosed <socket.socket fd=3, ...
    sock.close()
