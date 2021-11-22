import socket
import logging

from app.content.markers import Marker
from app.settings import HOST, PORT


class ServerError(Exception):
    pass


class ConnectionError(Exception):
    pass


class Dealer(Marker):
    def __init__(self, id, last_seen, bounding_box=None) -> None:
        super().__init__(id, last_seen, bounding_box=bounding_box)
        
        self.speed = 0
        self.turn = 0
        self.dealing = False
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((HOST, PORT))
            self.conn = None
        except socket.error as e:
            logging.error(e)
            raise ServerError("Server Error")
            
        finally:
            self.socket.close()
        
    def connect(self) -> None:
        logging.info("Paring with dealer...")
        try:
            self.socket.listen()
            self.conn, addr = self.socket.accept()
            logging.info('Connected by', addr)
        except socket.error as e:
            logging.error(e)
            raise ConnectionError("Couldn't connect with dealer")
        
    def send_data(self):
        data = str(int(self.dealer_speed)) + "," + str(int(self.dealer_turn_rate)) + "," + str(int(self.dealing))
        try:
            self.conn.sendall(data.encode())
        except socket.error as e:
            logging.error(e)
            return False
        
    