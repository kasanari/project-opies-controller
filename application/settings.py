import json

DEFAULT_SETTINGS = {
    "lookahead": 1,
    "checkpoint_threshold": 0.75,
    "goal_threshold": 0.35,
    "generate_movie": True,
    "kalman": {
        "dim_u": 1,
        "dim_x": 8,
        "update_delay": 0.1,
        "process_dev_pos": 0,
        "process_dev_acc": 0.08,
        "process_dev_heading": 0.0,
        "process_dev_heading_acc": 0.08,
        "process_dev_vel": 0.1,
        "meas_dev_pos": 0.3,
        "meas_dev_heading": 0.08,
        "meas_dev_acc": 1.2,
        "speed_div_by_length": 0.9,
        "variable_dt": True
    },
    "path": {
        "x": [],
        "y": []
    },
    "pid": {
      "steering": {
        "enable_d": False,
        "enable_i": False,
        "p": 1,
        "d": 0.1,
        "i": 0.01
      },
      "speed": {
          "enable_d": False,
          "enable_i": False,
          "p": 1,
          "d": 0.1,
          "i": 0.01
      }
    }
}

def load_default_settings():
   return DEFAULT_SETTINGS

def load_settings(filename):
    settings = load_default_settings()
    with open(filename) as f:
        try:
            loaded_settings = json.load(f)
        except json.JSONDecodeError as e:
            print(e)
            print(f"Loading {filename} failed, using default settings.")
            return settings
    for key in loaded_settings:
        if key not in settings.keys():
            print(f"Invalid settings key: {key}")
        else:
            settings[key] = loaded_settings[key]

    return settings


