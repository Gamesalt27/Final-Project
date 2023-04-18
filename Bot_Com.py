import socket
from Utils import *
import threading
from queue import Queue
import time
import random
import sys

SERVER_IP = "::1"
SERVER_TCP_PORT = 21212
DEST_MAC = "107B444CE6B2"
TEMP_MACs = ["000000000001", "000000000002", "000000000003"]
receive_MAC = Queue()           # (MAC, holepunch_port)
receive_data = Queue()          # load
send_MAC = Queue()              # (MAC, load)
send_data = Queue()             # (MAC, load, holepunch_port)
send_threads = Queue(MAX_SEND_THREADS_COUNT)



def main():         # for testing only
   pass 
   
       
def com_loop():                                 # TODO: add check for botnet ttl
    MAC = sys.argv[1]
    TEMP_MACs.remove(MAC)
    send_msg = bool(int(sys.argv[2]))
    server = threading.Thread(target=server_listener, args=((socket.socket(socket.AF_INET6, socket.SOCK_STREAM), (SERVER_IP, SERVER_TCP_PORT), MAC)))
    server.start()
    receive_thread = threading.Thread(target=receive_from_node, args=(SERVER_IP, MAC))
    receive_thread.start()
    send_thread = threading.Thread(target=send_to_node, args=(SERVER_IP, MAC))
    send_thread.start()
    if send_msg:                                                                                            # for testing
        ttl = 5
        endpoint = sys.argv[4]
        load = f"{ttl}${endpoint}$meow"
        send_MAC.put((sys.argv[3], load))
    while True:
        time.sleep(0.01)
        if receive_data.empty():
            continue
        load = receive_data.get(block=False)
        data, dst_MAC = proccess_msg(load)
        if type(data) == int:
            logging.info("load endpoint reached")
            continue
        logging.debug(f"sending {data} to {dst_MAC}")
        send_MAC.put((dst_MAC, data))


def send_to_node(server_IP: str, src_MAC: str):
    while True:
        time.sleep(0.01)
        if send_data.empty():
            continue
        dst_MAC, load, holepunch_port = send_data.get(block=False)
        logging.debug(f"retrived {dst_MAC}, {load} from send data Queue")
        with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as server:
            succeeded = UDP_send(server, (server_IP, holepunch_port), f"{src_MAC}${dst_MAC}")
            logging.debug(f"UDP sent {src_MAC}${dst_MAC} to {(server_IP, holepunch_port)}")
            msg = UDP_recieve(server, (server_IP, holepunch_port))
            logging.debug(f"UDP received {msg} from {(server_IP, holepunch_port)}")
            if not check_msg(msg):
                logging.info(f"{msg} didn't pass the check")
                pass
            IP, port = msg.split("$")
            port = int(port)
            logging.debug(f"holepunching to ({IP}, {port}) from {(server_IP, holepunch_port)}")
            client = holepunch(server, (IP, port))
            if client is None:
                continue
            succeeded = UDP_send(client, (IP, port), load)


def receive_from_node(server_IP: str, dst_MAC: str):
    while True:
        time.sleep(0.01)
        if receive_MAC.empty():
            continue
        src_MAC, holepunch_port = receive_MAC.get(block=False)
        with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as server:
            succeeded = UDP_send(server, (server_IP, holepunch_port), f"{src_MAC}${dst_MAC}")
            logging.debug(f"UDP sent {src_MAC}${dst_MAC} to {(server_IP, holepunch_port)}")
            msg = UDP_recieve(server, (server_IP, holepunch_port))              # IP and port for holepunching
            logging.debug(f"UDP received {msg} from {(server_IP, holepunch_port)}")
            if not check_msg(msg):
                logging.info(f"{msg} didn't pass the check")
                pass
            IP, port = msg.split("$")
            port = int(port)
            client = holepunch(server, (IP, port))
            if client is None:
                continue
            msg = UDP_recieve(client, (IP, port))
            if check_msg(msg):
                receive_data.put(msg) 


def server_listener(server: socket.socket, server_address: tuple, MAC: str):
    try:
        server.connect(server_address)
        logging.info(f"connected to {server.getpeername()[:2]}, from {server.getsockname()[:2]}")
        succeeded = TCP_send(server, MAC)
    except socket.error as e:
        logging.debug(f"server {server_address} unavaliable")
        return
    server.settimeout(SOCKET_TIMEOUT)
    while True:
        time.sleep(0.01)
        msg = TCP_recieve(server)
        if check_msg(msg):
            src_MAC, holepunch_port = msg.split("$")
            receive_MAC.put((src_MAC, int(holepunch_port)))
            logging.debug(f"TCP received {msg} from {server.getpeername()[:2]}")
        if send_MAC.empty(): continue
        MAC, data = send_MAC.get(block=False)
        logging.debug(f"retrived {MAC}, {data} from send MAC Queue")
        succeeded = TCP_send(server, MAC)
        msg = TCP_recieve(server)                       # msg - holepunch port TODO: deal with race condition with server sending wrong data
        if check_msg(msg):
            logging.debug(f"TCP received {msg} from {server.getpeername()[:2]}")
            send_data.put((MAC, data, int(msg)  ))
            logging.debug(f"put {MAC}, {data} in send data Queue")


def proccess_msg(msg: str):              # msg formats: ttl$endpoint$load, load
    if msg.find("$") == -1:
        return (1, "")
    msg = msg.split("$")
    ttl, endpoint, load = msg
    if int(ttl) <= 0:
        return (load, endpoint)
    ttl = int(ttl) - 1
    next_MAC = random.choice(TEMP_MACs)
    return (f"{ttl}${endpoint}${load}", next_MAC)
    
        

if __name__ == "__main__":
    com_loop()
