import cv2
import cv2.aruco as aruco
import numpy as np

from .aruco import ArucoFinder

def main():
    cv2.namedWindow("Video")
    cap = cv2.VideoCapture(0)
    aruco_finder = ArucoFinder()

    while True:
        ret, img = cap.read()
        bounding_boxes, ids = aruco_finder.find_aruco_markers(img)

        # if len(bounding_boxes) != 0:
        #     print(tuple(bounding_boxes[0][0][0].astype(int)))
        #     cv2.rectangle(img, tuple(bounding_boxes[0][0][0].astype(int)), tuple(bounding_boxes[0][0][2].astype(int)),
        #                   (255, 0, 0), 2)

        cv2.imshow("Video", img)
        cv2.waitKey(1)


