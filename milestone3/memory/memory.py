import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "chat_store.json")

def load_chats():

    if not os.path.exists(FILE_PATH):
        return {}, {}

    try:
        with open(FILE_PATH, "r") as f:
            data = json.load(f)

        # handle old format
        if isinstance(data, dict) and "chats" not in data:
            return data, {}

        return data.get("chats", {}), data.get("titles", {})

    except:
        return {}, {}


def save_chats(chats, titles):

    with open(FILE_PATH, "w") as f:
        json.dump({
            "chats": chats,
            "titles": titles
        }, f, indent=4)