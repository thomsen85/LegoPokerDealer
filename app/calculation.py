import math

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
    