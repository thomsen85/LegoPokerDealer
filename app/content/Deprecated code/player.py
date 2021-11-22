class Player:
    def __init__(self, id, bounding_box, last_seen):
        self.id = id
        self.bounding_box = bounding_box
        self.last_seen = last_seen

        self.dealt_cards = False
        self.is_dealer = id == 0

        self.turn = 0

    def update(self, bounding_box, last_seen):
        self.bounding_box = bounding_box
        self.last_seen = last_seen
