import json

DEFAULT_SETTINGS = {
    "lookahead": 1,
    "checkpoint_threshold": 0.75,
    "goal_threshold": 0.35,
    "generate_movie": True,
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
    settings = load_default_settings()
    with open(filename) as f:
        try:
            loaded_settings = json.load(f)
        except json.JSONDecodeError:
            print(f"Loading {filename} failed, using default settings.")
            return settings
    for key in loaded_settings:
        if key not in settings.keys():
            print(f"Invalid settings key: {key}")
        else:
            settings[key] = loaded_settings[key]

    return settings


