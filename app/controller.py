import cv2
from math import sqrt

from app.players import Player


def bounding_box_to_point(bounding_box, corners=4):
    bounding_box = bounding_box[0] # rid useless dimensions 
    x_sum = 0
    y_sum = 0
    for point in bounding_box:
        x_sum += point[0]
        y_sum += point[1]
    
    return (int(x_sum/corners), int(y_sum/corners))


class Controller:
    def __init__(self):
        self.players = {}
        self.dealer = None
        self.player_turns =[]

    def draw(self, img):
        for id in self.players:
            cv2.circle(img, bounding_box_to_point(self.players[id].bounding_box), 50, (255, 180, 255), -1)
            cv2.putText(img, str(id), bounding_box_to_point(self.players[id].bounding_box), cv2.FONT_ITALIC, 1, (0,0,0),5) 


        cv2.circle(img, bounding_box_to_point(self.dealer.bounding_box), 50, (0, 0, 255), -1)

    def update_player_list(self, players):
        for id in players:
            if players[id].is_dealer:
                self.dealer = players[id]
            else:
                self.players[id] = players[id]

    def update_player_turns(self):
        self.player_turns =[]
        bottom_left_most = 0
        lowest_dist = 10000

        for id in self.players:

            center = bounding_box_to_point(self.players[id].bounding_box)
            dist_from_tl = sqrt(center[0]**2 + center[1]**2)

            if dist_from_tl < lowest_dist:
                bottom_left_most = id
                lowest_dist = dist_from_tl
        
        print(bottom_left_most)

        
        





    
    