import cv2
import cv2.aruco as aruco
import numpy as np
import time

from .aruco import ArucoFinder
from .players import PlayerFinder


def main():
    cap = cv2.VideoCapture(0)
    aruco_finder = ArucoFinder()
    player_finder = PlayerFinder()

    while True:
        ret, img = cap.read()
        bounding_boxes, ids = aruco_finder.find_aruco_markers(img)

        player_finder.update()

        cv2.imshow("Video", img)
        cv2.waitKey(1)


