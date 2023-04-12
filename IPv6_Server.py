from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.http import Raw
import typing
import socket
import threading
from Utils import *
import time

notifications = {}                                  # typing.Dict[str, (bool, str)] TODO: cleanup irrelevent entries
connections = [threading.Thread]
holepunch_buddies = []                              # (str, str)
lock = threading.Lock()


def main():
    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.bind(('::1', 21212))
    holepunch_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    holepunch_socket.bind(('::1', 12121))
    receive_clients(server)


def receive_clients(server: socket.socket, holepunch_socket: socket.socket):
    server.listen()
    logging.info(f"server is listening on {server.getsockname()}")
    holepunch_connections = threading.Thread(target=holepunch_listener, args=(holepunch_socket))
    holepunch_connections.start()
    while True:
        client, adderess = server.accept()
        logging.info(f"new client connected {adderess}")
        msg = TCP_recieve(client)                      # TODO: parse msg (contains only MAC right now)
        notifications.update({msg: (False, "")})
        connections.append(threading.Thread(target=handle_client, args=(client, msg)))
        connections[-1].start()                          # TODO: add computer to main list


def handle_client(client: socket.socket, MAC="000000000000"):
    set_keepalive(client)
    logging.info(f"listening to client {client.getpeername()} on {client.getsockname()}")
    while True:
        msg = TCP_recieve(client)
        if not check_msg:
            client.close()
            return
        logging.info(f"received msg {msg} from {client.getpeername()}")
        set_notify(msg, True)
        succeeded = TCP_send(client, f"Succeeded")
        notified, src_MAC = is_notified(MAC)
        if notified:
            notify_client(client, src_MAC, MAC)


def holepunch_listener(holepunch_socket: socket.socket):
    while True:
        msg, address1 = UDP_recieve(holepunch_socket)             # msg is {source MAC}${destination MAC}
        addresses = msg.split("$")                  
        if addresses in holepunch_buddies:
            start_time = time.time()
            while time.time() - start_time < 10.0:
                time.sleep(0.1)
                msg, address2 = UDP_recieve(holepunch_socket)
                if msg.split("$") != addresses:
                    continue
                send_credentials(holepunch_socket, address1, address2)


def send_credentials(holepunch_socket: socket.socket, src_address, dst_address):
    succeeded = UDP_send(holepunch_socket, src_address, f"{dst_address[0]}${dst_address[1]}")
    succeeded = UDP_send(holepunch_socket, dst_address, f"{src_address[0]}${src_address[1]}")
                

def notify_client(client: socket.socket, src_MAC: str, dst_MAC: str):
    succeeded = TCP_send(client, dst_MAC)
    holepunch_buddies.append((src_MAC, dst_MAC))


def set_notify(src_MAC: str, notification: bool, dst_MAC: str):
    with lock:
        notifications[src_MAC] = (notification, dst_MAC)


def is_notified(MAC: str):
    with lock:
        if notifications[MAC][0]:
            notifications[MAC] = (False, "")
            return notifications[MAC]
        return False

    

if __name__=="__main__":
    main()   