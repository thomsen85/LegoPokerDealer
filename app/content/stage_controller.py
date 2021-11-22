from enum import Enum, auto


class StageController():
    def __init__(self) -> None:
        self.stage = Stage.START_POS
    
    def next() -> None:
        pass
    
    def reset() -> None:
        pass
    
    def get_current_task() -> str:
        pass
    
    def get_dealer_data():
        pass
    
    


class Stage(Enum):
    START_POS = 0
    ALIGNING = 1
    DRIVING = 2
    ALIGNING_NORMALY = 3
    
    
'''
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
            
    ###Stages###
    def start_play_stage(self):
        if self.dealer_cam_status_color == "green" and self.dealer_socket_status_color == "green":
            self.login_stage = False
            self.play_stage = True
            self.player_finder.joining_stage = False
            
            self.controller.update_players(self.player_finder.players)
            self.controller.start_new_game()
        else:
            messagebox.showerror(title="Connection Error", message="Make sure the dealer is connected before you start the game")

    ###Controller###
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
        
'''