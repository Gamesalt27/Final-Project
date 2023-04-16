import socket
from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.http import Raw
from Utils import *
from Botnet_Protocol import Botnet_Packet
import threading
from Botnet_Protocol import Botnet_Packet
from queue import Queue
import time
import random
import sys

SERVER_IP = "::1"
SERVER_TCP_PORT = 21212
SERVER_UDP_PORT = 12121
DEST_MAC = "107B444CE6B2"
TEMP_MACs = ["000000000001", "000000000002", "000000000003"]
receive_MAC = Queue()           # MAC
receive_data = Queue()          # load
send_MAC = Queue()              # (MAC, load)
send_data = Queue()             # (MAC, load)
send_threads = Queue(MAX_SEND_THREADS_COUNT)



def main():         # for testing only
   pass 
   
       
def com_loop():                                 # TODO: add check for botnet ttl
    MAC = sys.argv[1]
    TEMP_MACs.remove(MAC)
    send_msg = bool(int(sys.argv[2]))
    server = threading.Thread(target=server_listener, args=((socket.socket(socket.AF_INET6, socket.SOCK_STREAM), (SERVER_IP, SERVER_TCP_PORT), MAC)))
    server.start()
    receive_thread = threading.Thread(target=receive_from_node, args=((SERVER_IP, SERVER_UDP_PORT), MAC))
    receive_thread.start()
    send_thread = threading.Thread(target=send_to_node, args=((SERVER_IP, SERVER_UDP_PORT), MAC))
    send_thread.start()
    if send_msg:                                                                                            # for testing
        send_MAC.put((sys.argv[3], "Meow"))
    while True:
        time.sleep(0.01)
        if receive_data.empty():
            continue
        load = receive_data.get(block=False)
        data = proccess_msg(load)
        dst_MAC = random.choice(TEMP_MACs)
        logging.debug(f"sending {data} to {dst_MAC}")
        send_MAC.put((dst_MAC, data))


def send_to_node(server_address: tuple, src_MAC: str):
    while True:
        time.sleep(0.01)
        if send_data.empty():
            continue
        dst_MAC, load = send_data.get(block=False)
        logging.debug(f"retrived {dst_MAC}, {load} from send data Queue")
        with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as server:
            succeeded = UDP_send(server, server_address, f"{src_MAC}${dst_MAC}")
            #logging.debug(f"UDP sent {MAC} to {server.getpeername()[:1]}")
            msg = UDP_recieve(server, server_address)
            logging.debug(f"UDP received {msg} from {server.getpeername()[:2]}")
            if not check_msg(msg):
                pass
            IP, port = msg.split("$")
            logging.debug(f"holepunching to ({IP}, {port}) from {server.getsockname()[:2]}")
            client = holepunch(server, (IP, port))
            if client is None:
                continue
            succeeded = UDP_send(client, (IP, port), load)


def receive_from_node(server_address: tuple, dst_MAC: str):
    while True:
        time.sleep(0.01)
        if receive_MAC.empty():
            continue
        src_MAC = receive_MAC.get(block=False)
        with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as server:
            succeeded = UDP_send(server, server_address, f"{src_MAC}${dst_MAC}")
            #logging.debug(f"UDP sent {MAC} to {server.getpeername()[:1]}")
            msg = UDP_recieve(server, server_address)
            logging.debug(f"UDP received {msg} from {server.getpeername()[:2]}")
            if not check_msg(msg):
                pass
            IP, port = msg.split("$")
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
            receive_MAC.put(msg)
            logging.debug(f"TCP received {msg} from {server.getpeername()[:2]}")
        if send_MAC.empty(): continue
        MAC, data = send_MAC.get(block=False)
        logging.debug(f"retrived {MAC}, {data} from send MAC Queue")
        succeeded = TCP_send(server, MAC)
        msg = TCP_recieve(server)
        if check_msg(msg):
            pass
        logging.debug(f"TCP received {msg} from {server.getpeername()[:2]}")
        if msg == "Succeeded":
            send_data.put((MAC, data))
            logging.debug(f"put {MAC}, {data} in send data Queue")


def proccess_msg(msg: str):              # TODO: intilize
    return msg
        

if __name__ == "__main__":
    com_loop()
