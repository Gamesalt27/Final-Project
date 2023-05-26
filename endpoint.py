import socket
from Utils import *
import logging

SERVER_ERROR = """
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>503 Service Unavailable</title>
</head><body>
<h1>Service Unavailable</h1>
<p>Could not contact requested server.<br />
</p>
</body></html>
"""

def main():
    pass


def com_with_destination(load: str):
    IP, port, data = load.split("#")
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        soc.connect((IP, int(port)))
        soc.sendall(load.encode())
        data = soc.recv(1024).decode()
    except socket.error as e:
        return SERVER_ERROR
    return data


def write_to_file(data: str):
    page = data[data.find("<!DOCTYPE HTML"):]
    with open("website.html", "a+") as file:
        file.write(page)


if __name__ == "__main__":
    main()