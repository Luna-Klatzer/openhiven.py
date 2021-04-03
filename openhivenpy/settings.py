import pkg_resources
import os
from dotenv import load_dotenv
from openhivenpy.exceptions import HivenENVError


def load_env_vars() -> None:
    """ Loads the openhiven.py environment variables from the file openhivenpy.env """
    path = 'openhivenpy.env'
    env_path = pkg_resources.resource_filename(__name__, path)

    # Fetching the paths origin and finding the openhivenpy.env file
    load_dotenv(env_path)

    test_var = os.getenv("HIVEN_HOST")

    if test_var is None:
        raise HivenENVError(f"Failed to load .env file of the module! Expected {env_path} to exist")

