import socket
import logging


def UDP_send(destination: socket.socket, address: tuple, msg: bytes):
    try:
        destination.sendto(msg, address)
    except socket.Exception:
        logging.exception(f"can't send query to destination: {address}")
        return 
    return 1


def UDP_recieve(source: socket.socket, address: tuple):           # TODO: clear socket buffer after read
    try:
        msg, addr = source.recvfrom(1024)
    except TimeoutError:
        logging.debug(f"source {address} unavailable")
        return 0
    if addr != address:
        logging.warning(f"received from wrong address: expected {address}, got {addr}")
        return 1
    return decrypt(msg)


def TCP_recieve(source: socket.socket):           # TODO: clear socket buffer after read
    try:
        msg = source.recv(1024)
    except TimeoutError:
        logging.debug(f"source {source.getpeername()} unavailable")
        return 0
    return decrypt(msg)


def TCP_send(destination: socket.socket, msg: bytes):
    try:
        destination.sendall(msg)
    except socket.Exception:
        logging.exception(f"can't send query to destination: {destination.getpeername()}")
        return 
    return 1


def decrypt(msg: bytes):
    try:
        msg = msg.decode()
    except ValueError:
        logging.warning(f"failed to decode bytes: {msg}")
        return 2
    return msg


def holepunch(destination: socket.socket, address: tuple):
    for i in range(0, 9):
        succeeded = UDP_send(destination, address, b'hello there')
        if succeeded is None: return
        msg = UDP_recieve(destination, address)
        if msg == "hello there": break
    else:
        logging.info(f"unable to holepunch with {address}")
        return
    return 1


def set_keepalive(sock, after_idle_sec=60, interval_sec=60, max_fails=10):
    """Set TCP keepalive on an open socket.
    It activates after after_idle_sec of idleness,
    then sends a keepalive ping once every interval_sec,
    and closes the connection after max_fails failed ping ()
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)


def get_updates():      # TODO: define the function
    pass


def recieve_botnet_packet():
    pass
