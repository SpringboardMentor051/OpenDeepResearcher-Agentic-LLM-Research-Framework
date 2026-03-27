import json
import os

FILE_PATH = "milestone3/memory/chat_store.json"


def load_chats():
    if not os.path.exists(FILE_PATH):
        return {}

    with open(FILE_PATH, "r") as f:
        return json.load(f)


def save_chats(chats):
    with open(FILE_PATH, "w") as f:
        json.dump(chats, f, indent=4)