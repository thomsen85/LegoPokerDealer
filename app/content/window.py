import cv2
import PIL.Image, PIL.ImageTk

import tkinter as tk
import tkinter.font as font


class Window:
    '''
    GUI unit
    
    Params:
    ------
        - window: tk.Tk() window
        - window_title: name of window
    '''
    GRAY = "#2c2c2c"
    DARK = "#1c1c1c"

    def __init__(self, window, window_title):
 
        ### Window configs ####
        self.window = window
        self.window.title(window_title)
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.defaultFont = font.nametofont("TkDefaultFont")
        self.defaultFont.configure(family="Montserrat",
                                   size=18,
                                   weight=font.NORMAL)

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
        '''Main Loop'''
        self.update_listbox()
        self.window.after(self.delay, self.update)
    
    def update_listbox(self):
        pass
        '''
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
            
        '''
        
    
    '''Window components'''
    def update_middle_cards_button_press(self):
        self.update_middle_cards = True
        self.update_middle_cards_button_text.set("Click on video where\n to place")
        
    def update_middle_card_pos(self, event):
        if self.update_middle_cards:
            scaling =  self.camera.width / self.canvas_size[0] 
            self.controller.set_middle_card_pos(event.x * scaling, event.y * scaling)
            self.update_middle_cards = False
            self.update_middle_cards_button_text.set("Update Middle cards\n position")
            
    
    def on_closing(self):
        self.window.destroy()
        

def main():
    Window(tk.Tk(), "Poker Robot V1.0")
