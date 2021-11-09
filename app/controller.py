import cv2
import math
import socket

from .players import Player

HOST = 'localhost'  # local host
PORT = 8070

class Calculations:
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
    def bounding_box_to_front_point(bounding_box, front_shift_multiplier=1):
        bounding_box = bounding_box[0] # rid useless dimensions 
        x_sum = 0
        y_sum = 0
        for point in bounding_box[:2]:
            x_sum += point[0]
            y_sum += point[1]
        
        return (int(x_sum/2), int(y_sum/2))

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

        length = math.sqrt(x**2 +y**2)

        return ((x/length) * length_multiplier, (y/length) * length_multiplier)

    @staticmethod
    def get_dealer_angle_offset_to_player(dealer, player):
        player_x, player_y  = Calculations.bounding_box_to_front_point(player.bounding_box)
        dealer_x, dealer_y = Calculations.bounding_box_to_point(dealer.bounding_box)
        
        player_to_dealer_vector = (player_x - dealer_x, player_y - dealer_y) 
        player_to_dealer_rads = math.atan2(player_to_dealer_vector[0], player_to_dealer_vector[1]) + math.pi
        
        dealer_vector = Calculations.bounding_box_to_vector(dealer.bounding_box)
        dealer_rads = math.atan2(dealer_vector[0], dealer_vector[1]) 
        
        return (player_to_dealer_rads - dealer_rads)
    
    @staticmethod
    def get_distance_between_dealer_and_player(dealer, player):
        player_x, player_y  = Calculations.bounding_box_to_front_point(player.bounding_box)
        dealer_x, dealer_y = Calculations.bounding_box_to_point(dealer.bounding_box)
        
        return math.sqrt((player_x - dealer_x)**2 + (player_y - dealer_y)**2)
        
        
        

class Controller:
    def __init__(self):
        self.players = {}
        self.player_turns = []
        self.player_turn = 0
        
        '''Dealer stages'''
        self.start = False
        self.aligning = False
        self.drive_towards = False
        
        self.aligning_epsilon = 0.1
        self.proportional = 10
        
        self.dealer = None
        self.dealer_speed = 0
        self.dealer_turn_rate = 0

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.conn = None

    def draw(self, img):
        for id in self.players:
            circe_pos = Calculations.bounding_box_to_point(self.players[id].bounding_box)
            x_size, y_size = cv2.getTextSize(str(id), cv2.FONT_ITALIC, 1, 2)[0]
            text_pos = (circe_pos[0] - x_size//2, circe_pos[1] + y_size//2)

            cv2.circle(img, circe_pos, 35, (255, 180, 255), -1)
            cv2.putText(img, str(id), text_pos, cv2.FONT_ITALIC, 1, (0,0,0),2) 


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
            next_player = self.players[self.player_turns[self.player_turn]]
            diff_angle = Calculations.get_dealer_angle_offset_to_player(self.dealer, next_player)
            distance = Calculations.get_distance_between_dealer_and_player(self.dealer, next_player)
            
            if self.aligning:
                if abs(diff_angle) <= self.aligning_epsilon:
                    self.aligning = False
                else:
                    self.dealer_turn_rate = diff_angle * self.proportional
                    return f"Aligning to Player {self.player_turns[self.player_turn]}, degrees left: {round(diff_angle * (180/math.pi))}"
                
    

    def send_data_to_dealer(self):
        data = str(self.dealer_speed) + "," + str(self.dealer_turn_rate)
        try:
            self.conn.sendall(data.encode())
        except socket.error:
            return False
    
    def close(self):
        self.socket.close()

    
    


    