import pkg_resources
import os


def load_env():
    from dotenv import load_dotenv

    path = 'openhivenpy.env'
    env_path = pkg_resources.resource_filename(__name__, path)
    # Fetching the paths origin and finding the openhivenpy.env file
    load_dotenv(env_path)

    test_var = os.getenv("HIVEN_HOST")

    if test_var is None:
        print(f"[OPENHIVENPY] Failed to load .env file! Expected {env_path} to exist")
