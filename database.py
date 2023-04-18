from Utils import *
import logging
import json
import os


class database():           # handle for json db
    

    def __init__(self) -> None:
        try:
            file = open(DB_FILE, 'a+')
            file.close()
        except OSError as e:
            logging.critical("unable to create DB file")
            

    def add_client_entry(self, MAC: str, server: str, country: str, ret_flag=0):
        data = {'type': 2, 'MAC': MAC, 'server': server, 'country': country, 'ret_flag': ret_flag}
        logging.debug(f"adding {data} to db")
        try:
            with open(DB_FILE, 'a') as file:
                json.dump(data, file)
                file.write('\r\n')
        except OSError as e:
            logging.error(f"unable to write {data} to db")


    def add_server_entry(self, MAC: str, address: tuple):
        IP, port = address
        data = {'type': 1, 'MAC': MAC, 'IP': IP, 'port': port}
        logging.debug(f"adding {data} to db")
        try:
            with open(DB_FILE, 'a') as file:
                json.dump(data, file)
                file.write('\r\n')
        except OSError as e:
            logging.error(f"unable to write {data} to db")

    
    def remove_entry(self, MAC: str):
         with open(DB_FILE, "r+") as file:
            file.seek(0)
            for line in file.readlines:
                if json.loads(line)['MAC'] != MAC:
                    file.write(line)
                else:
                    logging.debug(f"removed {json.loads(line)} from db")
            file.truncate() 


def retrive_server(self, MAC: str):
        try:
            with open(DB_FILE, 'r') as file:
                file.seek(0)
                for line in file.readlines():
                    data = json.loads(line)
                    if data['MAC'] == MAC:
                        return (data['MAC'], (data['IP'], data['port']))
        except OSError as e:
             logging.error(f"unable to retrive {MAC} from db")


def retrive_client(self, MAC: str):
        try:
            with open(DB_FILE, 'r') as file:
                file.seek(0)
                for line in file.readlines():
                    data = json.loads(line)
                    if data['MAC'] == MAC:
                        return (data['MAC'], data['server'], data['country'], data['ret_flag'])
        except OSError as e:
             logging.error(f"unable to retrive {MAC} from db")


def next_ret(self):
    try:
        with open(DB_FILE, 'r') as file:
            file.seek(0)
            for line in file.readlines():
                data = json.loads(line)
                if data['ret_flag'] == 1:
                    return (data['MAC'], data['server'], data['country'])
    except OSError as e:
        logging.error(f"unable to read from db")


def reset_ret(self):
    with open(DB_FILE, "r+") as file:
            file.seek(0)
            for line in file.readlines:
                if json.loads(line)['ret_flag'] == 0:
                    file.write(line)
                else:
                    entry = json.loads(line)
                    entry['ret_flag'] = 0
                    file.write(json.dumps(entry))
                    logging.debug(f"removed {json.loads(line)} from db")
            file.truncate() 