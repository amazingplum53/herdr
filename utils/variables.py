import json
import os

def load_variables(stack, container_name = 'server'):

    if container_name == 'server':
        file_path = f"/server/{os.environ["PROJECT_NAME"]}/.config/env"
    else:
        file_path = f"/workspace/{os.environ["PROJECT_NAME"]}/.config/env"

    # Import variables from json file
    with open(f"{file_path}/{stack}.json", "r") as f:

        env_variables = json.loads(f.read())

        for name, value in env_variables.items():
            os.environ[name] = str(value)