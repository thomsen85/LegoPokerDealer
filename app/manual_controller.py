import socket
import arcade

HOST = '169.254.9.225'  # Standard loopback interface address (localhost)
PORT = 8070        # Port to listen on (non-privileged ports are > 1023)


class Window(arcade.Window):
    def __init__(self, title, width, height):
        super().__init__(title=title, width=width, height=height)
        arcade.set_background_color(arcade.color.AERO_BLUE)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.conn = None
        '''Controlls'''
        self.speed = 0
        self.turn = 0

        self.connect_to_robot()

    def on_draw(self):
        arcade.start_render()
        
        arcade.draw_text("Bruk piltastene", 10,10,color=(0,0,0), font_size=20)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol==arcade.key.UP:
           self.speed = 100 
        elif symbol==arcade.key.DOWN:
            self.speed = -100

        if symbol==arcade.key.RIGHT:
            self.turn = 100
        elif symbol==arcade.key.LEFT:
            self.turn = -100

        if symbol == arcade.key.ESCAPE:
            self.close()

        data = str(self.speed) + "," + str(self.turn)
        self.conn.send(data.encode())


    def on_key_release(self, symbol: int, modifiers: int):
        if symbol==arcade.key.UP:
           self.speed = 0
        elif symbol==arcade.key.DOWN:
            self.speed = 0

        if symbol==arcade.key.RIGHT:
            self.turn = 0
        elif symbol==arcade.key.LEFT:
            self.turn = 0

        data = str(self.speed) + "," + str(self.turn)
        self.conn.send(data.encode())

    def connect_to_robot(self):
        self.socket.bind((HOST, PORT))
        self.socket.listen()
        self.conn, addr = self.socket.accept()
        print('Connected by', addr)

    def close(self):
        self.socket.close()
        exit()
                


def controller():
    win = Window("Controller", 300, 50)
    win.run()
