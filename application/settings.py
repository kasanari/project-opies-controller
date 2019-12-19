import json

DEFAULT_SETTINGS = {
    "kalman": {
        "std_dev_acc": 0.8,
        "std_dev_position": 0.25,
        "std_dev_velocity": 0.8,
        "dim_u": 0,
        "dim_x": 6,
        "update_delay": 0.2
    },
    "path": {
        "x": [],
        "y": []
    }
}

def load_default_settings():
   return DEFAULT_SETTINGS

def load_settings(filename):
    with open(filename) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("Loading settings failed.")

