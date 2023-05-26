import socket
from Utils import *
import logging

def main():
    pass


def com_with_destination(load: str):
    IP, port, data = load.split("#")
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((IP, int(port)))
    soc.sendall(load.encode())
    data = soc.recv(1024).decode()
    return data


def write_to_file(data: str):
    with open("website.html", "a+") as file:
        file.write(data)


if __name__ == "__main__":
    main()