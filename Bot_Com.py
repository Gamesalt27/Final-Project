import socket
from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.http import Raw
import logging
from Utils import *
from Botnet_Protocol import Botnet_Packet

SERVER_IP = "127.0.0.1"
SERVER_PORT = 21212
DEST_MAC = "107B444CE6B2"


def main():
    pass


def send_to_node(address: tuple, packet: Botnet_Packet, MAC="000000000000"):  # TODO: deal with errors
    with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as server:
        server.bind((SERVER_IP, 0))
        addr = contact_IPv6server(server, address, MAC)
        if addr is int:
            match addr:
                case 0:
                    return
                case 1:
                    return
                case _:
                    return
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as destination:
            succeeded = holepunch(destination, addr)
            if succeeded is None:
                return
            packet.set_sport(server.getsockname()[1])
            packet.send()


def contact_IPv6server(server: socket.socket, address: tuple, MAC="000000000000"):
    succeeded = UDP_send(server, address, MAC.encode())
    if succeeded is None: return
    response = UDP_recieve(server)
    if response is not str: return response
    if len(response) != 8:
        logging.warning(f"response with wrong data {response} from {address}")
        return 2
    dest_IP, dest_port = response.split('$')  # TODO: check for incorrect response
    dest_port = int(dest_port)
    return (dest_IP, dest_port)


def server_listener(server: socket.socket):
    set_keepalive(server)
    server.connect()
    msg = server.recv(1024)


if __name__ == "__main__":
    main()
