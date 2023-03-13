from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.http import Raw
import typing
import logging
import socket
import threading
from Utils import *
import time

clients = {str: (bool, str, int)}                                  # TODO: cleanup irrelevent entries
connections = [threading.Thread]
lock = threading.Lock()

def main():
    Server = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

def receive_clients(server: socket.socket):
    server.listen()
    while True:
        client, adderess = server.accept()
        msg = TCP_recieve(client)                      # TODO: parse msg (contains only MAC right now)
        clients.update({msg: False})
        connections.append(threading.Thread(target=handle_client))
        connections[-1].start(client, msg)             # TODO: add computer to main list


def handle_client(client: socket.socket, MAC="000000000000"):
    set_keepalive(client)
    while True:
        time.sleep(1)
        msg =  TCP_recieve(client)
        if msg is int:
            if clients[MAC][0] == True:
                succeeded = TCP_send(client, f'{clients[MAC][2]}${clients[MAC][2]}')        # IP and Port with $ in between. TODO: check success
                notify_client(MAC, False)
                continue
        notify_client(msg, True, client.getpeername()[0], client.getpeername()[1])

                


def notify_client(MAC: str, notification: bool, IP='000.000.000.000', port=0):
    with lock:
        clients[MAC] = (notification, IP, port)
    

if __name__=="__main__":
    main()   