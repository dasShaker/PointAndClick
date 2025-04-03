import pygame
import json
import os
from room import Room
from player import Player
from item import Item


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "title"
        self.dt = 0
        self.selected_item = None
        self.font = pygame.font.Font(None, 24)

        self.assets = {
            "title_bg": pygame.Surface((640, 480)),
            "kitchen_bg": pygame.Surface((640, 480)),
            "hallway_bg": pygame.Surface((640, 480)),
            "knife": pygame.Surface((32, 32)),
            "rope": pygame.Surface((32, 32)),
            "key": pygame.Surface((32, 32)),
            "door": pygame.Surface((32, 64))
        }
        self.assets["title_bg"].fill((100, 100, 100))
        self.assets["kitchen_bg"].fill((150, 200, 255))
        self.assets["hallway_bg"].fill((150, 255, 150))
        self.assets["knife"].fill((255, 0, 0))
        self.assets["rope"].fill((139, 69, 19))
        self.assets["key"].fill((255, 255, 0))
        self.assets["door"].fill((100, 50, 0))

        self.buttons = {
            "new_game": pygame.Rect(200, 200, 240, 50),
            "load_game": pygame.Rect(200, 270, 240, 50),
            "quit": pygame.Rect(200, 340, 240, 50)
        }

        self.player = None
        self.rooms = {}
        self.inventory_offset = 0
        self.tooltip_text = None

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.state == "title":
                    if self.buttons["new_game"].collidepoint(pos):
                        self.start_new_game("game_config.json")
                    elif self.buttons["load_game"].collidepoint(pos):
                        self.load_game()
                    elif self.buttons["quit"].collidepoint(pos):
                        self.running = False
                elif self.state == "game":
                    if event.button == 1:  # Left-click
                        for i, item in enumerate(self.player.inventory):
                            item.rect.topleft = (10, 10 + i * 40 - self.inventory_offset)
                            if item.rect.collidepoint(pos):
                                self.selected_item = item
                                self.tooltip_text = f"{item.name}: {item.description}"
                                print(f"Selected {item.name}")
                                return
                        for obj in self.player.current_room.objects:
                            if obj.rect.collidepoint(pos):
                                if self.selected_item:
                                    obj.use(self.selected_item, self.player, self)
                                    self.selected_item = None
                                else:
                                    print(f"Clicked {obj.name}")
                                    if obj.name in self.player.current_room.exits:
                                        self.player.current_room = self.rooms[self.player.current_room.exits[obj.name]]
                                        print(f"Moved to {self.player.current_room.name}")
                                    else:
                                        self.player.inventory.append(obj)
                                        self.player.current_room.objects.remove(obj)
                    elif event.button == 3:  # Right-click
                        for i, item in enumerate(self.player.inventory):
                            if item.rect.collidepoint(pos):
                                self.tooltip_text = f"{item.name}: {item.description}"
                                break
                        else:
                            self.tooltip_text = None

            elif event.type == pygame.MOUSEWHEEL and self.state == "game":
                self.inventory_offset = max(0, min(self.inventory_offset - event.y * 20, max(0, len(self.player.inventory) * 40 - 200)))

    def update(self):
        if self.state == "game":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_s]:
                self.save_game()

    def draw(self):
        if self.state == "title":
            self.screen.blit(self.assets["title_bg"], (0, 0))
            pygame.draw.rect(self.screen, (0, 255, 0), self.buttons["new_game"])
            pygame.draw.rect(self.screen, (0, 0, 255), self.buttons["load_game"])
            pygame.draw.rect(self.screen, (255, 0, 0), self.buttons["quit"])
        elif self.state == "game":
            self.player.current_room.draw(self.screen)
            inventory_area = pygame.Rect(0, 0, 100, 480)
            pygame.draw.rect(self.screen, (50, 50, 50), inventory_area)
            for i, item in enumerate(self.player.inventory):
                item.rect.topleft = (10, 10 + i * 40 - self.inventory_offset)
                if inventory_area.collidepoint(item.rect.center):
                    item.draw(self.screen)
            if self.tooltip_text:
                tooltip = self.font.render(self.tooltip_text, True, (255, 255, 255))
                self.screen.blit(tooltip, (110, 10))
        pygame.display.flip()

    def start_new_game(self, config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
        self.player = Player()
        self.rooms = {}
        for room_name, data in config["rooms"].items():
            self.rooms[room_name] = Room(room_name, self.assets[data["bg"]], data.get("state"))
            self.rooms[room_name].game = self
            for item in data.get("items", []):
                self.rooms[room_name].objects.append(
                    Item(item["name"], item["x"], item["y"], self.assets[item["image"]],
                         item.get("description", ""), item.get("interactions", {}))
                )
            if "exits" in data:
                self.rooms[room_name].exits = data["exits"]
        self.player.current_room = self.rooms[config["start_room"]]
        self.state = "game"

    def save_game(self):
        save_data = {
            "current_room": self.player.current_room.name,
            "inventory": [{"name": item.name, "x": item.rect.x, "y": item.rect.y, "state": item.state} for item in self.player.inventory],
            "rooms": {}
        }
        for room_name, room in self.rooms.items():
            save_data["rooms"][room_name] = {
                "objects": [
                    {"name": obj.name, "x": obj.rect.x, "y": obj.rect.y, "state": obj.state}
                    for obj in room.objects
                ],
                "exits": room.exits,
                "state": room.state
            }
        with open("savegame.json", "w") as f:
            json.dump(save_data, f)
        print("Game saved!")

    def load_game(self):
        if os.path.exists("savegame.json"):
            with open("savegame.json", "r") as f:
                save_data = json.load(f)
            self.player = Player()
            self.rooms = {}
            with open("game_config.json", "r") as f:
                config = json.load(f)
            for room_name, data in config["rooms"].items():
                self.rooms[room_name] = Room(room_name, self.assets[data["bg"]], data.get("state"))
                self.rooms[room_name].game = self
                if "exits" in data:
                    self.rooms[room_name].exits = data["exits"]
            for room_name, room_data in save_data["rooms"].items():
                self.rooms[room_name].objects = [
                    Item(obj["name"], obj["x"], obj["y"], self.assets[obj["name"]],
                         config["rooms"][room_name]["items"][i].get("description", ""),
                         config["rooms"][room_name]["items"][i].get("interactions", {}),
                         obj.get("state"))
                    for i, obj in enumerate(room_data["objects"])
                ]
                self.rooms[room_name].exits = room_data["exits"]
                self.rooms[room_name].state = room_data["state"]
            self.player.current_room = self.rooms[save_data["current_room"]]
            for item_data in save_data["inventory"]:
                self.player.inventory.append(
                    Item(item_data["name"], item_data["x"], item_data["y"], self.assets[item_data["name"]],
                         state=item_data.get("state"))
                )
            self.state = "game"
            print("Game loaded!")
        else:
            print("No save file found!")


if __name__ == "__main__":
    game = Game()
    game.run()
