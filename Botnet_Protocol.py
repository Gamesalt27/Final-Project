from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.http import Raw
import logging
from Utils import *
from random import randint


class Botnet_Packet:

    packet = IP()/UDP()/Raw()

    def __init__(self, dest_IP: str, dest_port: int, src_port: int, payload_packet, end_IP: str, end_port: int, end_MAC="000000000000"):
        self.packet.dst = dest_IP
        self.packet.sport = src_port
        self.packet.dport = dest_port
        self.packet.id = randint(4, 32)
        self.packet.load = end_MAC.encode() + '$'.encode() + end_IP.encode() + '$'.encode() + str(end_port).encode() + '$'.encode() + bytes(payload_packet)
        self.packet.show()

    def send(self):
        pass
        
    def set_sport(self, port: int):
        self.packet.sport = port


def main():
    pac = Botnet_Packet("127.0.0.1", 1234, 1234, IP()/TCP()/Raw(), "127.0.0.1", 1234)
       

if __name__ == "__main__":
    main()
