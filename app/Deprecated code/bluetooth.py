# system_profiler SPBluetoothDataType
# https://blog.kevindoran.co/bluetooth-programming-with-python-3/

# Mac: 0C:E4:41:D9:94:38
# EV3Dev: 00:17:E9:B2:F6:62

import socket
import time


def bluetooth():
    HOST = '169.254.9.225'  # Standard loopback interface address (localhost)
    PORT = 8070        # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                conn.sendall(b"Heisann")
                time.sleep(1)