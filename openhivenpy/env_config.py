import logging
import os
from typing import Optional, Dict, List, Any, Tuple

import pkg_resources
from dotenv import load_dotenv

from openhivenpy.exceptions import HivenENVError

__all__ = ['HivenENV']

logger = logging.getLogger(__name__)


class HivenENV:
    """
    Class used to store the openhivenpy env_vars and functions used to
    load/unload files
    """
    ENV_VAR_KEYS: List[str] = [
        'HIVEN_HOST', 'HIVEN_API_VERSION', 'USER_TOKEN_LEN', 'BOT_TOKEN_LEN',
        'WS_HEARTBEAT', 'WS_CLOSE_TIMEOUT', 'WS_ENDPOINT'
    ]
    _env_vars: Optional[Dict[str, Any]] = None

    @property
    def env_vars(self) -> Dict[str, Any]:
        return self._env_vars

    def unload_env(self) -> None:
        """ Unloads all openhiven.py environment variables. """
        for elem in self.ENV_VAR_KEYS:
            if os.environ.get(elem) is not None:
                del os.environ[elem]

    def load_env_file(self, path: str) -> Tuple[Dict[str, Any], bool]:
        """
        Loads the file specified and will return True if it succeeded else
        False

        :param path: Path of the .env file
        :returns: The loaded env_vars in a dictionary format and bool if it was
         successful
        """
        self.unload_env()
        try:
            if load_dotenv(path, verbose=True, override=True):
                logger.debug(f"Loaded {path} as .env file")
                return dict(
                    (item, os.getenv(item)) for item in self.ENV_VAR_KEYS
                    if os.getenv(item) is not None
                ), True
        except Exception:
            ...

        logger.debug(f"Ignoring failed load of {path} as .env file")
        return dict((item, None) for item in self.ENV_VAR_KEYS), False

    def load_default_env(self):
        """ Loads the default library environment file """
        name = 'openhivenpy.env'
        env_path = pkg_resources.resource_filename(__name__, name)

        env_vars, success = self.load_env_file(env_path)
        # If the load failed it will return False
        if success:
            self._env_vars = env_vars
            return env_vars
        else:
            raise HivenENVError(
                f"Failed to load .env file of the module! "
                f"Expected {env_path} to exist"
            )

    def load_env(
            self, path: Optional[str] = None, search_other: bool = True
    ) -> dict:
        """
        Unloads pre-existing openhiven.py-related variables and attempts to
        load the env-variables from the library file openhivenpy.env

        Default function that will be called when importing the openhiven.py
        module. This function will attempt to find an env file in the workdir
        and if it exists that one will be loaded instead. This can be turned
        off by setting search_other to False.

        If certain variables are missing in the file the defaults of the
        library will be used to avoid issues while running.

        :param path: Optional path that can be passed to load a specific .env
         file. If the file does not contain all data it will default to loading
         the standard file. Defaults to None => searching for other files if
         search_other is True else defaulting to using the library .env file
        :param search_other: If set to True the function will try to find a
         file that ends with .env in the execution directory. It will attempt
         to load it and find all required env variables. If the file does not
         contain them, it will default to the standard library .env file. To
         avoid this set search_other to False which will automatically default
         to the base file and not load any file.
        :raises HivenENVError: If the function failed to default back to the
         openhiven.env file and all loading attempts were unsuccessful
        :returns: The loaded environment dictionary
        """
        self.load_default_env()
        if path is not None:
            env_vars, success = self.load_env_file(path)
            if success:
                self._env_vars.update(env_vars)
                return env_vars

        if search_other:
            path = os.getcwd()

            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.env'):
                        env_path = os.path.join(root, file)

                        logger.debug(
                            f"Found {env_path} as .env file. "
                            f"Attempting to load file "
                        )
                        env_vars, success = self.load_env_file(env_path)
                        if success:
                            self._env_vars.update(env_vars)
                            return env_vars
                        else:
                            # Unloading the environment variables since the
                            # file is not in the right format
                            self.unload_env()
                            self.load_default_env()
