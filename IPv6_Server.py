from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.http import Raw
import typing
import socket
import threading
from Utils import *
import time

notifications = {}                                  # typing.Dict[str, typing.Tuple[bool, str, int]], TODO: cleanup irrelevent entries
clients = {}                                        # typing.Dict[str, typing.Tuple[str, int]]
connections = [threading.Thread]
lock = threading.Lock()


def main():
    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.bind(('::1', 21212))
    receive_clients(server)


def receive_clients(server: socket.socket):
    server.listen()
    logging.info(f"server is listening on {server.getsockname()}")
    while True:
        client, adderess = server.accept()
        logging.info(f"new client connected {adderess}")
        msg = TCP_recieve(client)                      # TODO: parse msg (contains only MAC right now)
        notifications.update({msg: (False, None, None)})
        clients.update({msg: client.getpeername()[:2]})
        connections.append(threading.Thread(target=handle_client, args=(client, msg)))
        connections[-1].start()                          # TODO: add computer to main list
        logging.debug(str(clients))


def handle_client(client: socket.socket, MAC="000000000000"):
    set_keepalive(client)
    logging.info(f"listening to client {client.getpeername()} on {client.getsockname()}")
    while True:
        time.sleep(1)
        print(1)
        msg = TCP_recieve(client)
        print(2)
        if msg is int:
            print(3)
            if clients[MAC][0] == True:
                logging.info(f"notifying client {MAC} to connect to {notifications[MAC]}")
                succeeded = TCP_send(client, f"{notifications[MAC][1]}${notifications[MAC][2]}")        # IP and Port with $ in between. TODO: check success
                notify_client(MAC, False)
            continue
        logging.info(f"received msg {msg} from {client.getpeername()}")
        notify_client(msg, True, client.getpeername()[0], client.getpeername()[1])
        succeeded = TCP_send(client, f"127.0.0.1${clients[msg][1]}")
        print(4)


def notify_client(MAC: str, notification: bool, IP='000.000.000.000', port=0):
    with lock:
        notifications[MAC] = (notification, IP, port)
    

if __name__=="__main__":
    main()   