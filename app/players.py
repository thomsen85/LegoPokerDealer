import cv2
import cv2.aruco as aruco
import numpy as np
import time

def get_element_in_nested_list(iter, item):
    results = []
    for n in iter:
        if item == n[0]:
            results.append(item)
    
    return results

def element_in_nested_list(iter, item):
    if iter == None:
        return False

    for n in iter:
        if item == n[0]:
            return True
    
    return False

class PlayerFinder:
    TIMEOUT_TIME = 10
    JOINING_TIME = 3

    def __init__(self):
        self.players = []
        self.joining = []

    def update(self, bounding_boxes, ids):
        if len(bounding_boxes) != 0:
            for id in ids:
                if not (element_in_nested_list(self.joining, id) or element_in_nested_list(self.players, id)):
                    print(f"{id} is a new player, waiting to join")
                    self.joining.append([id, time.time()])
                    continue

        if len(self.joining) != 0:
            for player in self.joining:
                if not element_in_nested_list(ids, player[0]):
                    self.joining.remove(player)
                    print(f"{player[0]} was removed from the joining.")
                elif time.time() - player[1] >= self.JOINING_TIME and not element_in_nested_list(self.players, player[0]):
                    self.players.append([player[0],time.time()])
                    self.joining.remove(player)
                    print(f"{player[0]} added to the player list.")
                    continue

        if len(self.players) != 0:
            for player in self.players:
                if element_in_nested_list(ids, player[0]):
                    player[1] = time.time()
                elif time.time() - player[1] >= self.TIMEOUT_TIME:
                    self.players.remove(player)
                    print(f"Player {player[0]} timed out.")
                    

                elif time.time() - player[1] >= self.TIMEOUT_TIME/2:
                    print(f"Player {player[0]} is about to time out.")

