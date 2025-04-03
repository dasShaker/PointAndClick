class Room:
    def __init__(self, name, bg_image, state=None):
        self.name = name
        self.background = bg_image
        self.objects = []
        self.exits = {}
        self.game = None
        self.state = state  # e.g., "locked", "flooded"

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        for obj in self.objects:
            obj.draw(surface)
