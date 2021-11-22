import time

class Register:
    def __init__(self) -> None:
        
        self.dealer = None
        
        self.players = {}
        self.joining = {}
        
        self.joining_stage = True
        
    def update(self, bounding_boxes, ids):
        '''
        Will update the register with new information. If the attribute joining_stage = False it wil not let people join. 
        
        Params:
        ------
            - bounding_boxes: array of bounding_boxes found, can be empty.
            - ids: array of ids, same order as bounding boxes, can be empty.
        '''
        
        if len(ids) == 0:
            return None
        
        ### Register new players into joining list ###
        if self.joining_stage:
            for id, bounding_box in zip(ids, bounding_boxes):
                if not (id in self.players or id in self.joining):
                    # print(f"{id} is a new player, waiting to join")
                    self.joining[id] = Player(id, bounding_box, time.time())

        ### Transfering to player list ###
        if len(self.joining) != 0:
            for player in list(self.joining):
                if not player in ids:
                    self.joining.pop(player)

                elif time.time() - self.joining[player].last_seen >= self.JOINING_TIME and not player in self.players:
                    self.players[player] = self.joining[player]
                    self.joining.pop(player)


        ### Removing from players when marker is missing for given time ###
        if len(self.players) != 0:
            for player in list(self.players):
                if player in ids:
                    index = np.where(ids==player)[0][0]
                    self.players[player].update(bounding_boxes[index], time.time())

                elif time.time() - self.players[player].last_seen >= self.TIMEOUT_TIME:
                    self.players.pop(player)

