import cv2
from math import sqrt

from app.players import Player
import math




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
            dist_from_tl = sqrt(center[0]**2 + center[1]**2)

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

        length = sqrt(x**2 +y**2)

        return ((x/length) * length_multiplier, (y/length) * length_multiplier)



class Controller:
    def __init__(self):
        self.players = {}
        self.dealer = None
        self.player_turns = []
        self.player_turn = 0

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

    def update_player_list(self, players):
        for id in players:
            if players[id].is_dealer:
                self.dealer = players[id]
            else:
                self.players[id] = players[id]

    def update_player_turns(self):
        first_player = Calculations.get_top_left_player(self.players)
        self.player_turns = Calculations.get_clockwise_turns(self.players, first_player)
    
    


    