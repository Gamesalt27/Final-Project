from Utils import *
import logging
import json
import os
import threading


class database():           # handle for json db
    
    MIN_SERVER_COUNT = 3
    MAX_ENTRIES = 60
    DB_FILE = r'db.txt'

    lock = threading.Lock()
    current_db = None
    current_temp = None

    def __init__(self, db_num: int):
        self.current_db = f"{db_num}{self.DB_FILE}"
        self.current_temp = f"{db_num}temp.txt"
        try:
            file = open(self.current_db, 'a+')
            file.close()
        except OSError as e:
            logging.critical("unable to create DB file")
            

    def add_client_entry(self, MAC: str, server: str, country: str, ret_flag=0):
        #if self.entry_count >= self.MAX_ENTRIES:
        #    return False
        with self.lock:
            data = {'type': 2, 'MAC': MAC, 'server': server, 'country': country, 'ret_flag': ret_flag}
            logging.debug(f"adding {data} to db")
            try:
                with open(self.current_db, 'a') as file:
                    json.dump(data, file)
                    file.write("\n")
            except OSError as e:
                logging.error(f"unable to write {data} to db")
                return False
            return True   


    def add_server_entry(self, MAC: str, address: tuple):
        with self.lock:
            IP, port = address
            data = {'type': 1, 'MAC': MAC, 'IP': IP, 'port': port}
            logging.debug(f"adding {data} to db")
            try:
                with open(self.current_db, 'a') as file:
                    json.dump(data, file)
                    file.write("\n")
            except OSError as e:
                logging.error(f"unable to write {data} to db")

    
    def remove_entry(self, MAC: str):
        with self.lock:
            with open(self.current_db, "r") as input:
                with open(self.current_temp, "w") as output:
                    for line in input:
                        if json.loads(line.strip("\n"))['MAC'] != MAC:
                            output.write(line)
            os.replace(self.current_temp, self.current_db)


    def retrive_server(self, MAC: str):
        with self.lock:
            try:
                with open(self.current_db, 'r') as file:
                    file.seek(0)
                    for line in file.readlines():
                        data = json.loads(line)
                        if data['MAC'] == MAC:
                            return (data['MAC'], (data['IP'], data['port']))
            except OSError as e:
                logging.error(f"unable to retrive {MAC} from db")


    def retrive_client(self, MAC: str):
        with self.lock:
            try:
                with open(self.current_db, 'r') as file:
                    file.seek(0)
                    for line in file.readlines():
                        data = json.loads(line)
                        if data['MAC'] == MAC:
                            return (data['MAC'], data['server'], data['country'], data['ret_flag'])
            except OSError as e:
                logging.error(f"unable to retrive {MAC} from db")


    def next_ret(self):
        with self.lock:
            try:
                with open(self.current_db, 'r') as file:
                    file.seek(0)
                    for line in file.readlines():
                        data = json.loads(line)
                        if data['ret_flag'] == 1:
                            return data['MAC']
            except OSError as e:
                logging.error(f"unable to read from db")


    def reset_ret(self, MAC: str):
        data = self.retrive_client(MAC)
        self.remove_entry(MAC)
        self.add_client_entry(MAC, data[1], data[2])
    

    def count_entries(self):
        with self.lock:
            try:
                with open(self.current_db, 'r') as file:
                    file.seek(0)
                    return len(file.readlines())
            except OSError as e:
                logging.error(f"unable to read from db")


    def retrive_MACs(self, type: int):
        with self.lock:
            try:
                with open(self.current_db, 'r') as file:
                    file.seek(0)
                    MACs = [json.loads(line)['MAC'] for line in file.readlines() if json.loads(line)['type'] == type]
                    return MACs    
            except OSError as e:
                logging.error(f"unable to read from db")
        

    def set_ret(self, MAC: str):
        with self.lock:
            try:
                with open(self.current_db, "r") as input:
                    with open(self.current_temp, "w") as output:
                        for line in input:
                            if json.loads(line.strip("\n"))['MAC'] != MAC:
                                output.write(line)
                            else:
                                data = json.loads(line)
                                data['ret_flag'] = 1
                                json.dump(data, output)
                                output.write("\n")
            except ValueError or OSError as e: pass
            os.replace(self.current_temp, self.current_db)


    def entry_exists(self, MAC: str):
        with self.lock:
            try:
                with open(self.current_db, 'r') as file:
                    file.seek(0)
                    for line in file.readlines():
                        if json.loads(line)["MAC"] == MAC: return True
            except ValueError or OSError as e:
                logging.error(f"unable to read from db")
        return False
