import boto3
from botocore.exceptions import ClientError
import json
import os

SECRETS_FILE_NAME = "secrets"
AWS_SECRET_NAME = "prod-secrets"
PROJECT_NAME = os.getenv("PROJECT_NAME")
FILE_PATH = f"/server/{PROJECT_NAME}/.config/secret"


def get_secret(secret_name: str = AWS_SECRET_NAME) -> str:
    """Fetch a secret from AWS Secrets Manager."""
    region_name = "eu-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        return None

    secret = get_secret_value_response.get('SecretString', None)

    if not secret:
        print("No secret found or it's binary data.")
        return None
    else:
        print("Secrets fetched - saving to system")

    return secret


def create_secret_file(secret_json: str, file_name: str = SECRETS_FILE_NAME):
    """Write secrets to a .env file."""
    try:
        secrets = json.loads(secret_json)  # Ensure the secret is a JSON object
    except json.JSONDecodeError:
        print("Secret is not a valid JSON string.")
        return

    os.makedirs(FILE_PATH, exist_ok=True)

    with open(f"{FILE_PATH}/{file_name}.json", 'w') as f:
        json.dump(secrets, f, indent=4)

    output = ""

    for key, value in secrets.items():
        output += f'export {key}="{value}"\n'

    with open(f"{FILE_PATH}/{file_name}.source", "w") as f:
        f.write(output)

    print(f"Files created at {FILE_PATH}")


def load_secrets_file(file_name: str = SECRETS_FILE_NAME):

    try:
        secrets = {}

        with open(f"{FILE_PATH}/{file_name}.json", "r") as f:
            secrets = json.loads(f.read())

    except json.JSONDecodeError:
        print("Secret is not a valid JSON string.")
        return  

    if secrets:
        for key, value in secrets.items():
            os.environ[key] = value
        print("Secrets loaded")


def handle_secrets(stack):

    if not os.path.exists(f"{FILE_PATH}/{SECRETS_FILE_NAME}.json"): 
        try:
            print(f"Fetching {stack} secrets")

            if stack == "local":
                secret_name = "dev" # Change this to (STACK + user_name) for multiple local environs
            else:
                secret_name = stack

            secrets = get_secret(secret_name)
            create_secret_file(secrets)
            load_secrets_file()

            print(f"Secrets Resolved")
        except Exception as e:
            print("secrets not loaded:" + str(e))
    else:
        load_secrets_file()


if __name__ == "__main__":

    handle_secrets("prod")

