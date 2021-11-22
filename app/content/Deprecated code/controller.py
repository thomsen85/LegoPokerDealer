import cv2
import math
import socket
from time import time

from .player_finder import Player
from .calculation import Calculations

HOST = 'localhost'  # local host
PORT = 8070

class Controller:
    def __init__(self):
        ### Players ###
        self.players = {}
        self.player_turns = []
        self.player_turn = 0
        self.deal_area_front_shift = 100
        
        ### Error Margin ###
        self.aligning_epsilon = 0.08
        self.distance_epsilon = 20
        
        ### Clamps ###
        self.max_speed = 100
        self.max_turn_rate = 200
        
        ### Proportional controller ###
        self.proportional_turn = -60
        
        ### Dealer ###
        self.dealer = None
        self.dealer_speed = 0
        self.dealer_turn_rate = 0
        self.dealing = False
        self.normal_angle = -math.pi/2
        self.deal_time = 6
        self.started_dealing = None
        
        ### Dealer stages ##
        self.start = False
        self.aligning = False
        self.drive_towards = False
        self.align_normally = False
        self.deal_cards = False
        self.deal_middle_cards = False
        self.finished = False
        
        ### Middle cards ###
        self.middle_card_spacing = 80
        self.middle_card_x = 1920//2
        self.middle_card_y = 1080//2
        self.update_middle_cards = False
        self.middle_card_points = [(self.middle_card_x + (i*self.middle_card_spacing), self.middle_card_y)for i in range(-2, 3)]
        self.middle_card_current_point = 0
        
        ### Socket Connection###
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.conn = None

    def draw(self, img):
        for id in self.players:
            circe_pos = Calculations.bounding_box_to_point(self.players[id].bounding_box)
            cv2.circle(img, circe_pos, 35, (255, 180, 255), -1)
            
            deal_pos = Calculations.bounding_box_to_front_point(self.players[id].bounding_box, self.deal_area_front_shift)
            cv2.circle(img, deal_pos, 10, (0, 0, 255), -1)
            
            x_size, y_size = cv2.getTextSize(str(id), cv2.FONT_ITALIC, 1, 2)[0]
            text_pos = (circe_pos[0] - x_size//2, circe_pos[1] + y_size//2)
            cv2.putText(img, str(id), text_pos, cv2.FONT_ITALIC, 1, (0,0,0),2) 
            
        ### MIDDLE CARDS ###
        for point in self.middle_card_points:
            cv2.circle(img, point, 5, (0, 255, 0), -1)

        if self.start:
            dealer_pos = Calculations.bounding_box_to_point(self.dealer.bounding_box)
            dealer_vec = Calculations.bounding_box_to_vector(self.dealer.bounding_box, 100)
            cv2.arrowedLine(img, dealer_pos, (dealer_pos[0] + int(dealer_vec[0]), dealer_pos[1] + int(dealer_vec[1])), (0, 0, 255), 5)
            
    '''Players'''
    def update_player_turns(self):
        first_player = Calculations.get_top_left_player(self.players)
        self.player_turns = Calculations.get_clockwise_turns(self.players, first_player)



    def update_players(self, players):
        for id in players:
            if players[id].is_dealer:
                self.dealer = players[id]
            else:
                self.players[id] = players[id]
                
        

    '''Dealer'''
    def connect_to_dealer(self):
        print("Paring...")
        try:
            self.socket.listen()
            self.conn, addr = self.socket.accept()
            print('Connected by', addr)
            return True
        except socket.error:
            print("Couldn't connect with dealer")
            return False
        
    def start_new_game(self):
        self.start = True
        self.aligning = True
        self.update_player_turns()
        self.player_turn = 0

        
    def update_data_to_dealer(self):
        if self.start:
            if self.player_turn >= len(self.player_turns) or self.deal_middle_cards:
                self.deal_middle_cards = True
                next_player = Player(self.middle_card_current_point+100, [Calculations.point_to_bounding_box(self.middle_card_points[self.middle_card_current_point], -10)],0)
                diff_angle = Calculations.get_dealer_angle_offset_to_player(self.dealer, next_player, 0)
                distance = Calculations.get_distance_between_dealer_and_player(self.dealer, next_player, 0)
                
                if self.middle_card_current_point > len(self.middle_card_points):
                    self.middle_card_current_point = 0  
                    self.player_turn = 0 
                    self.start = False
                    self.deal_middle_cards = False
            else:
                next_player = self.players[self.player_turns[self.player_turn]]
  
                diff_angle = Calculations.get_dealer_angle_offset_to_player(self.dealer, next_player, self.deal_area_front_shift)
                distance = Calculations.get_distance_between_dealer_and_player(self.dealer, next_player, self.deal_area_front_shift)

            ### Aligning stage ###
            if self.aligning:
                if abs(diff_angle) <= self.aligning_epsilon:
                    self.aligning = False
                    self.drive_towards = True
                else:
                    self.dealer_speed = 0
                    self.dealer_turn_rate = diff_angle * self.proportional_turn
                    if not self.deal_middle_cards:
                        return f"Aligning to Player {self.player_turns[self.player_turn]}, degrees left: {round((diff_angle) * (180/math.pi))}"
                    else:
                        return f"Aligning to Middle cards, degrees left: {round((diff_angle) * (180/math.pi))} "
            
            ### Driving stage ###    
            elif self.drive_towards:
                if distance < self.distance_epsilon:
                    self.drive_towards = False
                    self.align_normally = True
                else:
                    self.dealer_speed = self.max_speed/2
                    self.dealer_turn_rate = diff_angle * self.proportional_turn
                    if not self.deal_middle_cards:
                        return f"Driving to Player {self.player_turns[self.player_turn]}, distance left: {round(distance)}"
                    else:
                        return f"Driving to Middle cards, distance left: {round(distance)}"
                    
            ### Aligning normally to player stage ###
            elif self.align_normally:
                diff_angle = Calculations.get_dealer_angle_offset_to_player(self.dealer, next_player, -self.deal_area_front_shift)
                if abs((diff_angle - self.normal_angle)) <= self.aligning_epsilon:
                    self.align_normally = False
                    self.deal_cards = True
    
                    self.started_dealing = time()
                else:
                    self.dealer_speed = 0
                    self.dealer_turn_rate = (diff_angle - self.normal_angle) * self.proportional_turn
                    if not self.deal_middle_cards:
                        return f"Aligning normaly to Player {self.player_turns[self.player_turn]}, degrees left: {round(((diff_angle - self.normal_angle)) * (180/math.pi))}"
                    else:
                        return f"Aligning normaly to Middle card, deg left: {round(((diff_angle - self.normal_angle)) * (180/math.pi))} "

            ### Dealing stage ###
            elif self.deal_cards:
                if time() - self.started_dealing >= self.deal_time:
                    self.deal_cards = False
                    self.dealing = False
                    self.player_turn += 1
                    self.aligning = True
                    if self.deal_middle_cards:
                        self.middle_card_current_point += 1

                else:
                    self.dealing = True
                    self.dealer_speed = 0
                    self.dealer_turn_rate = 0
                    if not self.deal_middle_cards:
                        return f"Dealing cards to Player {self.player_turns[self.player_turn]}, finished in: {round(self.deal_time - (time() - self.started_dealing), 1)}"
                    else:
                        return f"Dealing to middle cards, finished in: {round(self.deal_time - (time() - self.started_dealing), 1)}"

                
                
    def send_data_to_dealer(self):
        data = str(int(self.dealer_speed)) + "," + str(int(self.dealer_turn_rate)) + "," + str(int(self.dealing))
        try:
            self.conn.sendall(data.encode())
        except socket.error:
            return False
        
    '''Middle cards'''
    def set_middle_card_pos(self, x, y):
        self.middle_card_x = int(x)
        self.middle_card_y = int(y)
        self.middle_card_points = [(self.middle_card_x + (i*self.middle_card_spacing), self.middle_card_y)for i in range(-2, 3)]
    