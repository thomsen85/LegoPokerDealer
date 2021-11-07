import cv2
import tkinter as tk
import tkinter.font as font
import tkinter.ttk as ttk
import PIL.Image, PIL.ImageTk

from .aruco import ArucoFinder
from .players import PlayerFinder
from .controller import Controller


class Window:
    GRAY = "#2c2c2c"
    DARK = "#1c1c1c"

    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.defaultFont = font.nametofont("TkDefaultFont")
  
        
        self.defaultFont.configure(family="Montserrat",
                                   size=18,
                                   weight=font.NORMAL)

        '''Own Modules'''
        self.camera = Webcamera()
        self.aruco_finder = ArucoFinder()
        self.player_finder = PlayerFinder()
        self.controller = Controller()

        '''Stages'''
        self.login_stage = True
        self.play_stage = False

        '''Window elements'''
        self.padding = 20

        self.canvas_size = (1152, 648)
        self.canvas = tk.Canvas(window, bd=0, width = self.canvas_size[0], height = self.canvas_size[1], relief=tk.RIDGE)
        self.canvas.grid(row=0, column=0, columnspan=4, padx=self.padding, pady=(self.padding, self.padding/2))

        self.listbox_label = tk.Label(window, text="Players:")
        self.listbox_label.grid(row=1, column=0, sticky="nsew")
        self.listbox = tk.Listbox(window, font=self.defaultFont)
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
        self.dealer_task_status_label = tk.Label(self.dealer_frame, textvariable=self.dealer_task, border=0, bg=self.DARK)
        self.dealer_task_status_label.pack(fill="x", anchor="n", pady=(0, self.padding))


        self.button = tk.Button(window, text="Start Game", bd=0, command=self.start_play_stage)
        self.button.grid(row=2, column=3)

        self.window.resizable(False, False)

        self.delay = 15
        self.update()
        self.window.mainloop()

    def start_play_stage(self):
        self.login_stage = False
        self.play_stage = True
        self.player_finder.joining_stage = False

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

    def update_listbox(self):
        players_joining = dict(self.player_finder.joining)
        players = dict(self.player_finder.players)

        # Clean list for dealer
        if 0 in players_joining:
            players_joining.pop(0)
        elif 0 in players:
            players.pop(0)

        if self.listbox.size() > 1:
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



    def update(self):

        ret, frame = self.camera.get_frame()

        bounding_boxes, ids = self.aruco_finder.find_aruco_markers(frame)

        if self.login_stage:
            if ids is None:
                self.player_finder.update([], [])
            else:
                self.player_finder.update(bounding_boxes, ids.flatten())
                

        elif self.play_stage:
            if ids is None:
                self.player_finder.update([], [])
            else:
                self.player_finder.update(bounding_boxes, ids.flatten())

            self.controller.update_player_list(self.player_finder.players)
            self.controller.draw(frame)
        
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), self.canvas_size)))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)

        self.update_listbox()
        self.update_dealer()
        self.window.after(self.delay, self.update)
        



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




'''
def main():
    cap = cv2.VideoCapture(0)
    aruco_finder = ArucoFinder()
    player_finder = PlayerFinder()
    controller = Controller()
    
    login_stage = True
    play_stage = False
    
    while True:
        ret, img = cap.read()
        bounding_boxes, ids = aruco_finder.find_aruco_markers(img)


        if login_stage:
            if ids is None:
                pass
            else:
                player_finder.update(bounding_boxes, ids.flatten())
                
            cv2.putText(img, "Joining Stage", (10,img.shape[0]-10), cv2.FONT_ITALIC, 2, (0,0,0),5) 

        elif play_stage:
            if ids is None:
                pass
            else:
                player_finder.update(bounding_boxes, ids.flatten())

            controller.update_player_list(player_finder.players)
            controller.draw(img)

            if cv2.waitKey(1) & 0xFF == ord('p'):
                controller.update_player_turns()

            pass

        cv2.imshow("Video", img)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            login_stage = False
            play_stage = True
            player_finder.joining_stage = False
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            controller.close()
            break
'''

def main():
    Window(tk.Tk(), "Poker Robot V1.0")
