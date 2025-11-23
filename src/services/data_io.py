import json
import os
import yaml

def read_json(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def write_json(data, file_path):
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def load_yaml_config(file_path):
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    return config