import json
from application.context import Context


def load_default_settings():
   return load_settings('default_settings.json')

def load_settings(filename):
    with open(filename) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("Loading settings failed.")

