import cv2.aruco as aruco
import cv2


class ArucoFinder:
    def __init__(self, marker_size=4, total_markers=250, draw=True):
        self.draw = draw

        key = getattr(aruco, f"DICT_{marker_size}X{marker_size}_{total_markers}")
        self.aruco_dict = aruco.Dictionary_get(key)
        self.aruco_params = aruco.DetectorParameters_create()

    def find_aruco_markers(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bounding_boxes, ids, rejected = aruco.detectMarkers(gray_img, self.aruco_dict, parameters=self.aruco_params)

        if self.draw:
            aruco.drawDetectedMarkers(img, bounding_boxes, ids)

        return bounding_boxes, ids
