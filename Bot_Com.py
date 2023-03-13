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
    succeeded = TCP_send(server, MAC.encode())
    if succeeded is None: return
    response = TCP_recieve(server)
    if response is not str: return response
    dest_IP, dest_port = response.split('$')  # TODO: check for incorrect response
    dest_port = int(dest_port)
    return (dest_IP, dest_port)


def server_listener(server: socket.socket, MAC="000000000000"):
    set_keepalive(server)
    server.settimeout(300)
    server.connect()
    succeeded = TCP_send(server, MAC.encode())
    while True:
        msg = TCP_recieve(server)
        if msg == 0:
            Succeeded = TCP_send(server, b'hello there')
            if Succeeded is None: pass          # TODO: switch to another server or close thread
            continue
        dest_IP, dest_port = msg.split('$')  # TODO: check for incorrect message
        dest_port = int(dest_port)
        return (dest_IP, dest_port)


def receive_from_node(address: tuple):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as source:
        succeeded = holepunch(source, address)
        if succeeded is None:
            return
        return recieve_botnet_packet()
        


if __name__ == "__main__":
    main()
