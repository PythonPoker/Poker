import json

json_file = "config/game.json"


def load_game_settings():
    with open(json_file, "r") as file:
        data = json.load(file)
    return data
