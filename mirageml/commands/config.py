import json
import os

def show_config():
    config = load_config()
    print(json.dumps(config, indent=4))

def load_config():
    config_path = os.path.expanduser("~/.mirageml.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "local_mode": False,
        "model": "gpt-4"
    }

def save_config(config):
    config_path = os.path.expanduser("~/.mirageml.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def set_config():
    config = load_config()

    valid = {
        "local_mode": ("(True, False)", bool),
        "model": ("(gpt-3.5-turbo, gpt-3.5-turbo-16k, gpt-4)", str)
    }

    print("Current configuration:")
    for key, value in config.items():
        print(f"{key}: {value}")

    print("\n")

    for key, value in config.items():
        while True:
            value = input(f"Enter the value for '{key}' {valid[key][0]} [{value}]: ")
            if value == "": break
            try: 
                value = valid[key][1](value)
            except:
                print(f"Invalid value for '{key}'. Please enter a value of type {valid[key][1]}")
                continue
            config[key] = value
            save_config(config)
            break

    print("MirageML Config updated!")
