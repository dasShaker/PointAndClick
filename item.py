import pygame


class Item:
    def __init__(self, name, x, y, image, description="", interactions=None, state=None):
        self.name = name
        self.rect = pygame.Rect(x, y, 32, 32) if name != "door" else pygame.Rect(x, y, 32, 64)
        self.image = image
        self.description = description or f"A {name}."
        self.interactions = interactions or {}
        self.state = state

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def use(self, other_item, player, game):
        if self.name in self.interactions and other_item.name in self.interactions[self.name]:
            action = self.interactions[self.name][other_item.name]
            print(f"Used {other_item.name} on {self.name}: {action}")
            if action == "cut":
                self.state = "cut"
                if self in player.current_room.objects:
                    player.current_room.objects.remove(self)
                elif self in player.inventory:
                    player.inventory.remove(self)
                player.current_room.objects.append(
                    Item("key", self.rect.x, self.rect.y + 40, game.assets["key"], "A shiny key.")
                )
                print("The rope falls away, revealing a key!")
            elif action == "unlock":
                self.state = "unlocked"
                if self.name in player.current_room.exits:
                    player.current_room.objects.remove(self)
                    print("The door is unlocked and opens!")
                else:
                    print("The door unlocks, but it doesn’t lead anywhere yet.")
        else:
            print("Nothing happens.")
