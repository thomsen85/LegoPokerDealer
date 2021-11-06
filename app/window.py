import cv2
import cv2.aruco as aruco
import numpy as np
import time

from .aruco import ArucoFinder
from .players import PlayerFinder
from .controller import Controller


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



