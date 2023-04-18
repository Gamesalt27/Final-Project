import socket
import logging
from scapy.all import *

MAX_SEND_THREADS_COUNT = 5
SOCKET_TIMEOUT = 1
DB_FILE = r'db.txt'
logging.basicConfig(level=logging.DEBUG)


def UDP_send(destination: socket.socket, address: tuple, msg: str):
    msg = encrypt(msg)
    try:
        destination.sendto(msg, address)
    except socket.error as e:
        logging.exception(f"can't send query to destination: {address}")
        return 
    return 1


def UDP_recieve(source: socket.socket, address=("", 0)):           # TODO: clear socket buffer after read
    try:
        msg, addr = source.recvfrom(1024)
    except socket.error as e:
        #logging.debug(f"source {address} unavailable")
        return 0
    if address == ("", 0):
        return (decrypt(msg), addr)
    if addr[:2] != address:
        logging.warning(f"received from wrong address: expected {address}, got {addr}")
        return 1
    return decrypt(msg)


def TCP_recieve(source: socket.socket):           # TODO: clear socket buffer after read
    try:
        msg = source.recv(1024)
    except socket.error as e:
        #logging.debug(f"source {source.getpeername()} unavailable")
        return 0
    clear_read_buffer(source)
    return decrypt(msg)


def TCP_send(destination: socket.socket, msg: str):
    msg = encrypt(msg)
    try:
        destination.sendall(msg)
    except socket.error as e:
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


def encrypt(msg: str):
    try:
        msg = msg.encode()
    except ValueError:
        logging.warning(f"failed to encode bytes: {msg}")
        return 2
    return msg


def holepunch(soc: socket.socket, address: tuple):
    for i in range(0, 9):
        succeeded = UDP_send(soc, address, "hello there")
        if succeeded is None:
            continue
        msg = UDP_recieve(soc, address)
        if msg == "hello there": break
    else:
        logging.info(f"unable to holepunch with ({address[0]}, {address[1]})")
        return
    return soc


def set_keepalive(sock: socket.socket, after_idle_sec=60, interval_sec=60, max_fails=10, timeout=5):
    """Set TCP keepalive on an open socket.
    It activates after after_idle_sec of idleness,
    then sends a keepalive ping once every interval_sec,
    and closes the connection after max_fails failed ping ()
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)
    sock.settimeout(timeout)


def get_updates():      # TODO: define the function
    pass


def receive_botnet_packet(src_address: tuple, dst_address: tuple):
    response = sniff(filter=f"dst host {dst_address[0]} and src host {src_address[0]} and udp dst port {dst_address[1]} and udp src port {src_address[1]}", count=1)
    return response[0].load.decode()

def clear_read_buffer(soc: socket.socket):
    soc.settimeout(0)
    try:
        while True: soc.recv(1024)
    except:
        pass
    soc.settimeout(SOCKET_TIMEOUT)


def check_msg(msg: str, type=0):
    return isinstance(msg, str)

