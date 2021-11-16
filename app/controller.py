import cv2
import math
import socket
from time import time

from .players import Player

HOST = '169.254.31.29'  # local host
PORT = 8070

class Calculations:
    @staticmethod
    def clamp_number(number, min_value, max_value):
        return max(min(number, max_value), min_value)
    
    @staticmethod
    def bounding_box_to_point(bounding_box, corners=4):
        bounding_box = bounding_box[0] # rid useless dimensions 
        x_sum = 0
        y_sum = 0
        for point in bounding_box:
            x_sum += point[0]
            y_sum += point[1]
        
        return (int(x_sum/corners), int(y_sum/corners))

    @staticmethod
    def bounding_box_to_front_point(bounding_box, front_shift_multiplier=0):
        bounding_box = bounding_box[0] # rid useless dimensions 
        x_sum = 0
        y_sum = 0
        for point in bounding_box[:2]:
            x_sum += point[0]
            y_sum += point[1]
        
        directional_vector = Calculations.bounding_box_to_vector([bounding_box], front_shift_multiplier)
        
        return (int(x_sum/2 + directional_vector[0]), int(y_sum/2 + directional_vector[1]))

    @staticmethod
    def get_top_left_player(players: dict):
        bottom_left_most = 0
        lowest_dist = 10000

        for id in players:

            center = Calculations.bounding_box_to_point(players[id].bounding_box)
            dist_from_tl = math.sqrt(center[0]**2 + center[1]**2)

            if dist_from_tl < lowest_dist:
                bottom_left_most = id
                lowest_dist = dist_from_tl

        return bottom_left_most

    @staticmethod
    def get_clockwise_turns(all_players: dict, first_player: int):
        players = list(all_players.values())
        players.remove(all_players[first_player])

        turns = [first_player]

        while len(players) > 0:
            min_player = None
            min_value = 7

            for player in players:
                x, y  = Calculations.bounding_box_to_front_point(player.bounding_box)
                origin_x, origin_y = Calculations.bounding_box_to_front_point(all_players[turns[-1]].bounding_box)
                rads = math.atan2(origin_x - x, y - origin_y) + math.pi
                if rads < min_value:
                    min_player =  player
                    min_value = rads
            
            turns.append(min_player.id)
            players.remove(min_player)

        return turns

    @staticmethod
    def bounding_box_to_vector(bounding_box, length_multiplier=1):
        bounding_box = bounding_box[0] # rid useless dimensions
        top_x_sum = 0
        top_y_sum = 0
        bottom_x_sum = 0
        bottom_y_sum = 0

        for point in bounding_box[:2]:
            top_x_sum += point[0]
            top_y_sum += point[1]
        
        for point in bounding_box[2:]:
            bottom_x_sum += point[0]
            bottom_y_sum += point[1]

        x = top_x_sum/2 - bottom_x_sum/2
        y = top_y_sum/2 - bottom_y_sum/2

        length = math.sqrt(x**2 + y**2)

        return ((x/length) * length_multiplier, (y/length) * length_multiplier)

    @staticmethod
    def get_dealer_angle_offset_to_player(dealer, player, player_front_shift=1):
        player_x, player_y  = Calculations.bounding_box_to_front_point(player.bounding_box, player_front_shift)
        dealer_x, dealer_y = Calculations.bounding_box_to_point(dealer.bounding_box)
        
        player_to_dealer_vector = (player_x - dealer_x, player_y - dealer_y) 
        dealer_vector = Calculations.bounding_box_to_vector(dealer.bounding_box)
        
        angle = math.atan2(player_to_dealer_vector[1], player_to_dealer_vector[0]) - math.atan2(dealer_vector[1], dealer_vector[0])
        
        if angle > math.pi:
            angle -= 2 * math.pi
        elif angle <= -math.pi:
            angle += 2 * math.pi
            
        return angle
    
    @staticmethod
    def get_distance_between_dealer_and_player(dealer, player, player_front_shift=1):
        player_x, player_y  = Calculations.bounding_box_to_front_point(player.bounding_box, player_front_shift)
        dealer_x, dealer_y = Calculations.bounding_box_to_point(dealer.bounding_box)
        
        return math.sqrt((player_x - dealer_x)**2 + (player_y - dealer_y)**2)
    
    @staticmethod
    def point_to_bounding_box(point, size):
        tl = (point[0] - size, point[1] - size)
        tr = (point[0] + size, point[1] - size)
        bl = (point[0] - size, point[1] + size)
        br = (point[0] + size, point[1] + size)

        return [tl , tr, bl, br]

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
    