import socket
from Utils import *
import threading
from queue import Queue
import time
import random
import sys
from database import database
from endpoint import *


receive_MAC = Queue()           # (MAC, holepunch_port)
receive_data = Queue()          # load
send_MAC = Queue()              # (MAC, load)
send_data = Queue()             # (MAC, load, holepunch_port)
endpoint_port = 80
endpoint_IP = "134.173.42.59"


db = database(sys.argv[1])


def main():         # for testing only
   pass 
   
       
def com_loop():                                 # TODO: add check for botnet ttl
    MAC = sys.argv[2]
    send_msg = bool(int(sys.argv[4]))
    server_MAC, server_address = choose_server(int(sys.argv[3]))
    server = threading.Thread(target=server_listener, args=((socket.socket(socket.AF_INET6, socket.SOCK_STREAM), server_address, MAC, server_MAC)))
    server.start()
    receive_thread = threading.Thread(target=receive_from_node, args=(server_address[0], MAC))
    receive_thread.start()
    send_thread = threading.Thread(target=send_to_node, args=(server_address[0], MAC))
    send_thread.start()
    if send_msg:                                                                                            # for testing
        ttl = 2
        endpoint = sys.argv[6]
        load = f"{ttl}${endpoint}${endpoint_IP}#{endpoint_port}#{get_http()}"
        send_MAC.put((sys.argv[5], load))
        logging.debug(f"added {load}, {sys.argv[5]} to send_MAC queue")
    while True:
        time.sleep(0.01)
        if receive_data.empty():
            continue
        load = receive_data.get(block=False)
        data, dst_MAC = proccess_msg(load, MAC)
        if dst_MAC == 'no_rets':
            write_to_file(data)
            logging.info('response recived')
            continue
        if type(data) == int:
            logging.info("load endpoint reached")
            data = com_with_destination(load)
            ret_msg = f'1${data}'
            receive_data.put(ret_msg)
            logging.debug(f"returning response {ret_msg}")
            continue
        logging.debug(f"sending {data} to {dst_MAC}")
        send_MAC.put((dst_MAC, data))
        s_MAC = db.retrive_client(dst_MAC)[1]
        if s_MAC != server_MAC:
            server_MAC, server_address = db.retrive_server(dst_MAC)
            server = threading.Thread(target=server_listener, args=((socket.socket(socket.AF_INET6, socket.SOCK_STREAM), server_address, MAC, server_MAC)))
            server.start()


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
                print(type(msg))
                print(len(msg.split('$')) != 2)
                if len(msg.split('$')) != 2:
                    db.set_ret(src_MAC)


def server_listener(server: socket.socket, server_address: tuple, MAC: str, server_MAC: str):
    try:
        server.settimeout(SOCKET_TIMEOUT)
        server.connect(server_address)
        logging.info(f"connected to {server.getpeername()[:2]}, from {server.getsockname()[:2]}")
        succeeded = TCP_send(server, MAC)
    except socket.error as e:
        logging.debug(f"server {server_address} unavaliable")
        return
    while True:
        time.sleep(0.01)
        msg = TCP_recieve(server)
        if check_msg(msg):
            src_MAC, holepunch_port = msg.split("$")
            if db.entry_exists(MAC): db.add_client_entry(MAC, server_MAC, None)
            receive_MAC.put((src_MAC, int(holepunch_port)))
            logging.debug(f"TCP received {msg} from {server.getpeername()[:2]}")
        if send_MAC.empty():
            continue
        dst_MAC, data = send_MAC.get(block=False)
        logging.debug(f"retrived {dst_MAC}, {data} from send MAC Queue")
        s_MAC = db.retrive_client(dst_MAC)
        s_MAC = s_MAC[1]
        if s_MAC != server_MAC:
            logging.info(f"switching from server {server_MAC} to server {s_MAC}")
            succeeded = TCP_send(server, "shutting down connection")
            send_MAC.put(dst_MAC, data)
            server.close()
            return
        succeeded = TCP_send(server, dst_MAC)
        msg = TCP_recieve(server)                       # msg - holepunch port TODO: deal with race condition with server sending wrong data
        if check_msg(msg):
            logging.debug(f"TCP received {msg} from {server.getpeername()[:2]}")
            send_data.put((dst_MAC, data, int(msg)))
            logging.debug(f"put {dst_MAC}, {data} in send data Queue")


def proccess_msg(msg: str, MAC: str):              # msg formats: ttl$endpoint$load, load, flag$load
    if msg.find("$") == -1:
        return (1, "")
    msg = msg.split("$")
    if len(msg) == 3:
        ttl, endpoint, load = msg
        if int(ttl) <= 0:
            if endpoint == MAC:
                return (1, "")
            return (load, endpoint)
        ttl = int(ttl) - 1
        flag = False
        payload = f"{ttl}${endpoint}${load}"
    elif len(msg) == 2:
        flag, load = msg
        payload = f"{flag}${load}"
    next_MAC = choose_next_node(bool(int(flag)))
    return (payload, next_MAC)
    

def choose_next_node(is_ret=False):
    if is_ret:
        MAC = db.next_ret()
        if MAC == 'no_rets': return MAC
        db.reset_ret(MAC)
        return MAC
    MACs = db.retrive_MACs(2)
               
    MAC = random.choice(MACs)
    return db.retrive_client(MAC)[0]       # return MAC and server
 

def choose_server(type=0):            # TODO: implement different states
    if type == 1:
        return db.retrive_server("100000000000")
    if type == 2:
        return db.retrive_server("200000000000")
    MACs = db.retrive_MACs(1)           
    MAC = random.choice(MACs)
    return db.retrive_server(MAC)       # return MAC and address


def get_http():
    with open("http_request.txt", "r") as file:
        return file.read()


if __name__ == "__main__":
    com_loop()
