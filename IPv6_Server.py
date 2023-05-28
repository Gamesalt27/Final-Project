from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.http import Raw
import typing
import socket
import threading
from Utils import *
import time

notifications = {}                                  # typing.Dict[str, (bool, str, int)] TODO: cleanup irrelevent entries
connections = [threading.Thread]
lock = threading.Lock()


def main():
    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.bind(('::', int(sys.argv[1])))
    receive_clients(server)


def receive_clients(server: socket.socket):
    logging.info(f"server is listening on {server.getsockname()}")
    while True:
        server.listen()
        client, adderess = server.accept()
        logging.info(f"new client connected {adderess}")    # TODO: set socket timeout and deal with the error
        msg = TCP_recieve(client)                      # TODO: parse msg (contains only MAC right now)
        logging.debug(f"client {client.getpeername()[:2]} sent {msg}")
        notifications.update({msg: (False, "", 0)})
        connections.append(threading.Thread(target=handle_client, args=((client, msg))))
        connections[-1].start()                          # TODO: add computer to main list


def handle_client(client: socket.socket, MAC="000000000000"):
    #set_keepalive(client)
    logging.info(f"listening to client {client.getpeername()[:2]} on {client.getsockname()[:2]}")
    client.settimeout(SOCKET_TIMEOUT)
    while True:
        msg = TCP_recieve(client)
        if check_msg(msg):
            logging.debug(f"TCP received {msg} from {client.getpeername()[:2]}")
            holepunch_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            holepunch_socket.bind(('::', 0))
            set_notify(msg, True, MAC, holepunch_socket.getsockname()[1])
            succeeded = TCP_send(client, str(holepunch_socket.getsockname()[1]))
            holepunch_server = threading.Thread(target=holepunch_listener, args=((holepunch_socket, (MAC, msg))))
            holepunch_server.start()
        elif msg == "shutting down connection":
            notifications.pop(MAC)
            client.close()
            return
        notified, src_MAC, holepunch_port = is_notified(MAC)
        if notified:
            logging.debug(f"{MAC} got notified by {src_MAC}")
            notify_client(client, src_MAC, holepunch_port)


def holepunch_listener(holepunch_socket: socket.socket, MACs: tuple):
    logging.debug(f"holepunch server is listening on {holepunch_socket.getsockname()[:2]}")
    msg, address1 = UDP_recieve(holepunch_socket)             # msg is {source MAC}${destination MAC} TODO: add a check before spliting to msg and address
    logging.debug(f"UDP received {msg} from {address1[:2]}")
    logging.debug(msg.split("$"))
    if check_msg(msg):
        if tuple(msg.split("$")) == MACs:
            msg, address2 = UDP_recieve(holepunch_socket)
            logging.debug(f"UDP received {msg} from {address2[:2]}")
            if tuple(msg.split("$")) == MACs:
                send_credentials(holepunch_socket, address1[:2], address2[:2])
                logging.debug(f"connecting {MACs} together")


def send_credentials(holepunch_socket: socket.socket, src_address, dst_address):
    succeeded = UDP_send(holepunch_socket, src_address[:2], f"{dst_address[0]}${dst_address[1]}")
    succeeded = UDP_send(holepunch_socket, dst_address[:2], f"{src_address[0]}${src_address[1]}")
                

def notify_client(client: socket.socket, src_MAC: str, holepunch_port: int):
    succeeded = TCP_send(client, f"{src_MAC}${holepunch_port}")
    


def set_notify(src_MAC: str, notification: bool, dst_MAC: str, holepunch_port: int):
    with lock:
        notifications[src_MAC] = (notification, dst_MAC, holepunch_port)
        logging.debug(f"notifications dict got updated {notifications}")


def is_notified(MAC: str):
    with lock:
        output = notifications[MAC]
        notifications[MAC] = (False, "", 0)
        return output

    

if __name__=="__main__":
    main()   