import cv2.aruco as aruco
import cv2
import numpy as np


class Scanner:
    def __init__(self, marker_size=4, total_markers=250, draw=True):
        self.draw = draw
        key = getattr(aruco, f"DICT_{marker_size}X{marker_size}_{total_markers}")
        self.aruco_dict = aruco.Dictionary_get(key)
        self.aruco_params = aruco.DetectorParameters_create()
        

    def find_aruco_markers(self, img):
        '''
        Get the bounding-boxes and ids of markers in given image
        
        Parameters:
            - img: a cv2 img
        
        Returns:
            - (bounding_boxes, ids)
        
        '''
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bounding_boxes, ids, rejected = aruco.detectMarkers(gray_img, self.aruco_dict, parameters=self.aruco_params)

        if self.draw:
            aruco.drawDetectedMarkers(img, bounding_boxes, ids)
        
        if ids is not None:
            bounding_boxes = tuple(map(lambda x: x.squeeze(), bounding_boxes))
            ids = ids.squeeze()

        
            
        return bounding_boxes, ids
