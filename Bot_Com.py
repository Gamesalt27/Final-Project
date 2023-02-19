import socket
from scapy.layers.all import ETHER, IP, UDP
import logging

SERVER_IP = "127.0.0.1"
SERVER_PORT = 21212
DEST_MAC = "107B444CE6B2"

def main():
    server = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    destination = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def contact_IPv6server(server: socket.socket, address: tuple(str, int), MAC="000000000000"):
    succeded = UDP_send(server, address, MAC.encode())
    if succeded is None: return
    response = UDP_recieve(server)
    if response is not str: return response
    if len(response) != 8:
        logging.warning(f"response with wrong data {response} from {address}")
    dest_IP, dest_port = response.split('$')        # TODO: check for incorrect response
    dest_port = int(dest_port)
    return (dest_IP, dest_port)
    
    
def holepunch(destination: socket.socket, address: tuple(str, int)):
    for i in range(0, 9):
        succeded = UDP_send(destination, address, b'hello there')
        if succeded is None: return
        msg = UDP_recieve(destination, address)
        if msg == "hello there": break
    else:
        logging.info(f"unable to holepunch with {address}")
        return
    return 1


def UDP_send(destination: socket.socket, address: tuple(str, int), msg: bytes):
    try:
        destination.sendto(msg, address)
    except socket.Exception:
        logging.exception(f"can't send query to destination: {address}")
        return 
    return 1


def UDP_recieve(source: socket.socket, address: tuple(str, int)):           # TODO: clear socket buffer after read
    try:
        msg, addr = source.recvfrom(1024)
    except TimeoutError:
        logging.debug(f"source {address} unavilable")
        return 0
    if addr != address:
        logging.warning(f"received from wrong address: expected {address}, got {addr}")
        return 1
    return decrypt(msg)


def decrypt(msg: bytes):
    try:
        msg = msg.decode()
    except ValueError:
        logging.warning(f"failed to decode bytes: {msg}")
        return 2
    return msg
    



if __name__=="__main__":
    main()