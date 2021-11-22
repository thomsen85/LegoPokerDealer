import numpy as np
import math


class Marker:
    def __init__(self, id, last_seen, bounding_box=None) -> None:
        self.bounding_box = bounding_box
        self.id = id
        self.last_seen = last_seen
    
    def update(self, id, bounding_box) -> None:
        self.bounding_box = bounding_box
        self.id = id
    
    @property
    def center_point(self):
        return np.mean(self.bounding_box, axis=0)
    
    @property
    def normalized_directional_vector(self):
        top_x_sum = 0
        top_y_sum = 0
        bottom_x_sum = 0
        bottom_y_sum = 0

        for point in self.bounding_box[:2]:
            top_x_sum += point[0]
            top_y_sum += point[1]
        
        for point in self.bounding_box[2:]:
            bottom_x_sum += point[0]
            bottom_y_sum += point[1]

        x = top_x_sum/2 - bottom_x_sum/2
        y = top_y_sum/2 - bottom_y_sum/2

        length = math.sqrt(x**2 + y**2)
        vector = np.array([(x/length), (y/length)])
        
        return vector
    
    
    def get_forward_point(self, front_shift=1):
        x_sum = 0
        y_sum = 0
        for point in self.bounding_box[:2]:
            x_sum += point[0]
            y_sum += point[1]
        
        directional_vector = self.normalized_directional_vector() * front_shift
        
        forward_point = np.array([int(x_sum/2), int(y_sum/2)]) + directional_vector
        
        return forward_point
    
    def get_distance_to_point(self, point):
        point_x, point_y  = point
        marker_x, marker_y = self.center_point
        
        return math.sqrt((point_x - marker_x)**2 + (point_y - marker_y)**2)
    
    def get_angle_to_point(self, point):
        point_x, point_y  = point
        marker_x, marker_y = self.center_point
        
        marker_to_point_vector = (point_x - marker_x, point_y - marker_y) 
        marker_vector = self.normalized_directional_vector
        
        angle = math.atan2(marker_to_point_vector[1], marker_to_point_vector[0]) - math.atan2(marker_vector[1], marker_vector[0])
        
        if angle > math.pi:
            angle -= 2 * math.pi
        elif angle <= -math.pi:
            angle += 2 * math.pi
            
        return angle
