import cv2
import PIL.Image, PIL.ImageTk

import tkinter as tk
import tkinter.font as font
import tkinter.messagebox as messagebox
import time

from .aruco import ArucoFinder
from .players import PlayerFinder
from .controller import Controller


class Window:
    GRAY = "#2c2c2c"
    DARK = "#1c1c1c"

    def __init__(self, window, window_title):
        '''Window Configs'''
        self.window = window
        self.window.title(window_title)
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.bind("<KeyPress>", self.on_key_press)
        self.window.bind("<KeyRelease>", self.on_key_release)
        

        self.defaultFont = font.nametofont("TkDefaultFont")
        self.defaultFont.configure(family="Montserrat",
                                   size=18,
                                   weight=font.NORMAL)

        '''Own Modules'''
        self.camera = Webcamera()
        self.aruco_finder = ArucoFinder()
        self.player_finder = PlayerFinder()
        self.controller = Controller()
        
        self.deal_flip = False

        '''Stages'''
        self.login_stage = True
        self.play_stage = False

        '''Window components'''
        self.padding = 20

        self.canvas_size = (960,540)
        self.canvas = tk.Canvas(window, bd=0, width = self.canvas_size[0], height = self.canvas_size[1], relief=tk.RIDGE)
        self.canvas.grid(row=0, column=0, columnspan=4, padx=self.padding, pady=(self.padding, self.padding/2))
        self.canvas.bind("<Button-1>", self.update_middle_card_pos)
        
        self.listbox_label = tk.Label(window, text="Players:")
        self.listbox_label.grid(row=1, column=0, sticky="nsew")
        self.listbox = tk.Listbox(window, font=self.defaultFont, width=10)
        self.listbox.grid(row=2, column=0, sticky="nsew", padx=(self.padding, self.padding), pady=(0,self.padding))
        self.listbox.config(highlightcolor=self.GRAY)

        self.dealer_label = tk.Label(window, text="Dealer:")
        self.dealer_label.grid(row=1, column=1,columnspan=2, sticky="nsew")

        self.dealer_frame = tk.Frame(window, bg=self.DARK ,border=1, borderwidth=1)
        self.dealer_frame.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=self.padding, pady=(0,self.padding))

        self.dealer_cam_label = tk.Label(self.dealer_frame, text="Camera connection:", bg=self.DARK)
        self.dealer_cam_label.pack(fill="x", anchor="n", pady=(self.padding/4, 0))

        self.dealer_cam_status = tk.StringVar()
        self.dealer_cam_status_color = "red" 
        self.dealer_cam_status_label = tk.Label(self.dealer_frame, textvariable=self.dealer_cam_status, border=0, bg=self.dealer_cam_status_color)
        self.dealer_cam_status_label.pack(fill="x", anchor="n", pady=(0, self.padding))

        self.dealer_socket_label = tk.Label(self.dealer_frame, text="Socket connection:", bg=self.DARK)
        self.dealer_socket_label.pack(fill="x", anchor="n")

        self.dealer_socket_status = tk.StringVar()
        self.dealer_socket_status.set("Offline")
        self.dealer_socket_status_color = "red" 
        self.dealer_socket_status_label = tk.Label(self.dealer_frame, textvariable=self.dealer_socket_status, border=0, bg=self.dealer_socket_status_color)
        self.dealer_socket_status_label.pack(fill="x", anchor="n", pady=(0, self.padding))

        self.dealer_task_label = tk.Label(self.dealer_frame, text="Next task:", bg=self.DARK)
        self.dealer_task_label.pack(fill="x", anchor="n")

        self.dealer_task = tk.StringVar()
        self.dealer_task.set("Waiting for connection...")
        self.dealer_task_status_label = tk.Label(self.dealer_frame, textvariable=self.dealer_task, border=0, bg=self.DARK,
                                                 justify=tk.CENTER, wraplength=250)
        self.dealer_task_status_label.pack(fill="x", anchor="n", pady=(0, self.padding))

        self.button_frame = tk.Frame(window)
        self.button_frame.grid(row=2, column=3, sticky="nsew", padx=(0,self.padding), pady=(0, self.padding))
        self.button_frame.grid_columnconfigure(0, weight=1)

        self.pair_button = tk.Button(self.button_frame, text="Pair with dealer", bd=0, command=self.connect_to_dealer)
        self.pair_button.grid(row=0, column=0, sticky="ew", padx=self.padding)

        self.update_middle_cards_button_text = tk.StringVar()
        self.update_middle_cards_button_text.set("Update Middle cards\n position")
        self.update_middle_cards_button = tk.Button(self.button_frame,textvariable=self.update_middle_cards_button_text,
                                                    bd=0, command=self.update_middle_cards_button_press)
        self.update_middle_cards_button.grid(row=1, column=0, sticky="ew", padx=self.padding, pady=self.padding)
        self.update_middle_cards = False

        self.start_button = tk.Button(self.button_frame, text="Start Game", bd=0, command=self.start_play_stage)
        self.start_button.grid(row=2, column=0, sticky="ew", padx=self.padding, pady= self.padding)

        

        self.delay = 10
        self.update()
        self.window.mainloop()
        
    def update(self):
        success, frame = self.camera.get_frame()
        bounding_boxes, ids = self.aruco_finder.find_aruco_markers(frame)

        ### LOGIN STAGE ###
        if self.login_stage:
            self.update_players(ids, bounding_boxes)
                
        ### PLAY STAGE ###
        elif self.play_stage:
            self.update_players(ids, bounding_boxes)
            self.controller.update_players(self.player_finder.players)

            task = self.controller.update_data_to_dealer()
            self.dealer_task.set(task)
            
            if not self.deal_flip:
                if not self.controller.send_data_to_dealer():
                    self.dealer_cam_status.set("Offline")
                    self.dealer_cam_status_color = "red"
                    self.dealer_cam_status_label.config(bg=self.dealer_cam_status_color)
                    
            if self.controller.dealing:
                self.deal_flip = True
            else:
                self.deal_flip = False
         
        ### Draw to screen ###
        self.controller.draw(frame)
        if success:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), self.canvas_size)))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
        
        self.update_listbox()
        self.update_dealer()
        self.window.after(self.delay, self.update)

    def update_players(self,ids, bounding_boxes):
        if ids is None:
            self.player_finder.update([], [])
        else:
            self.player_finder.update(bounding_boxes, ids.flatten())
            
    '''Stages'''
    def start_play_stage(self):
        if self.dealer_cam_status_color == "green" and self.dealer_socket_status_color == "green":
            self.login_stage = False
            self.play_stage = True
            self.player_finder.joining_stage = False
            
            self.controller.update_players(self.player_finder.players)
            self.controller.start_new_game()
        else:
            messagebox.showerror(title="Connection Error", message="Make sure the dealer is connected before you start the game")

    '''Controller'''
    def connect_to_dealer(self):
        top = tk.Toplevel()
        top.title('Connecting')
        tk.Message(top, text="Waiting for dealer", padx=20, pady=20).pack()

        if self.controller.connect_to_dealer():
            top.destroy()
            self.dealer_socket_status.set("Online")
            self.dealer_socket_status_color = "green"
        else:
            top.destroy()
            self.dealer_socket_status.set("Offline")
            self.dealer_socket_status_color = "red"
        
        self.dealer_socket_status_label.config(bg=self.dealer_socket_status_color)

    def update_dealer(self):
        if 0 in self.player_finder.joining:
            self.dealer_cam_status.set("Joining")
            self.dealer_cam_status_color = "purple"
        
        elif 0 in self.player_finder.players:
            self.dealer_cam_status.set("Online")
            self.dealer_cam_status_color = "green"
        
        else:
            self.dealer_cam_status.set("Offline")
            self.dealer_cam_status_color = "red"
        
        self.dealer_cam_status_label.config(bg=self.dealer_cam_status_color)
        
    def update_middle_cards_button_press(self):
        self.update_middle_cards = True
        self.update_middle_cards_button_text.set("Click on video where\n to place")
        
    def update_middle_card_pos(self, event):
        if self.update_middle_cards:
            scaling =  self.camera.width / self.canvas_size[0] 
            self.controller.set_middle_card_pos(event.x * scaling, event.y * scaling)
            self.update_middle_cards = False
            self.update_middle_cards_button_text.set("Update Middle cards\n position")
            

    '''Window components'''
    def update_listbox(self):
        players_joining = dict(self.player_finder.joining)
        players = dict(self.player_finder.players)

        # Clean list for dealer
        if 0 in players_joining:
            players_joining.pop(0)
        elif 0 in players:
            players.pop(0)

        if self.listbox.size() > 0:
            self.listbox.delete(0, self.listbox.size())

        for index, player in enumerate(players_joining):
            if self.player_finder.joining[player].is_dealer:
                self.listbox.insert(index, "Dealer")
            else:
                self.listbox.insert(index, f"Player {player}")

            self.listbox.itemconfig(index, {'bg':'purple'})


        for index, player in enumerate(players):
            if self.player_finder.players[player].is_dealer:
                self.listbox.insert(index, "Dealer")
            else:
                self.listbox.insert(index, f"Player {player}")

            self.listbox.itemconfig(index, {'bg':'green'})

    '''Window Key Controlls'''
    def on_key_press(self, event):
        key_pressed = event.keysym
        
        if key_pressed == "Right":
            self.controller.dealer_turn_rate = 100
        elif key_pressed == "Left":
            self.controller.dealer_turn_rate = -100
            
        if key_pressed == "Up":
            self.controller.dealer_speed = 100
        elif key_pressed == "Down":
            self.controller.dealer_speed = 100
            
    def on_key_release(self, event):
        key_pressed = event.keysym
        
        if key_pressed == "Right" or key_pressed == "Left":
            self.controller.dealer_turn_rate = 0

        if key_pressed == "Up" or key_pressed == "Down":
            self.controller.dealer_speed = 0
            
    def on_closing(self):
        self.controller.socket.close()
        self.window.destroy()
        

class Webcamera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)  
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            return (ret, frame)
        else:
            return None

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

def main():
    Window(tk.Tk(), "Poker Robot V1.0")
