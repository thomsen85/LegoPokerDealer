import time
import numpy as np

from .player import Player

class PlayerFinder:
    TIMEOUT_TIME = 25
    JOINING_TIME = 3

    def __init__(self, joining_stage=True):
        self.players = {}
        self.joining = {}
        self.joining_stage = joining_stage

    def update(self, bounding_boxes, ids):
        '''Register new players into joining list'''
        if len(ids) != 0 and self.joining_stage:
            for id, bounding_box in zip(ids, bounding_boxes):
                if not (id in self.players or id in self.joining):
                    # print(f"{id} is a new player, waiting to join")
                    self.joining[id] = Player(id, bounding_box, time.time())

        '''Transfering to player list'''
        if len(self.joining) != 0:
            for player in list(self.joining):
                if not player in ids:
                    self.joining.pop(player)
                    # print(f"{player} was removed from the joining queue.")

                elif time.time() - self.joining[player].last_seen >= self.JOINING_TIME and not player in self.players:
                    self.players[player] = self.joining[player]
                    self.joining.pop(player)
                    # print(f"{player} added to the player list.")

        '''Removing from players when marker is missing for given time'''
        if len(self.players) != 0:
            for player in list(self.players):
                if player in ids:
                    index = np.where(ids==player)[0][0]
                    self.players[player].update(bounding_boxes[index], time.time())

                elif time.time() - self.players[player].last_seen >= self.TIMEOUT_TIME:
                    self.players.pop(player)
                    #print(f"Player {player} timed out.")

                elif time.time() - self.players[player].last_seen >= self.TIMEOUT_TIME/2:
                    # print(f"Player {player} is about to time out.")
                    pass
