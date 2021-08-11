import logging
import os

import openhivenpy

logging.basicConfig(level=logging.DEBUG)

openhivenpy.env.load_env(search_other=False)
default_env_vars = openhivenpy.env.env_vars  # <== openhivenpy.env


class TestENV:
    CORRECT_PATH = f'{os.path.dirname(__file__)}\\correct.env'
    FALSE_PATH = f'{os.path.dirname(__file__)}\\false.env'

    def test_load(self):
        openhivenpy.env.load_env(search_other=False)  # <== openhivenpy.env
        assert default_env_vars == openhivenpy.env.env_vars

    def test_find(self):
        openhivenpy.env.load_env(search_other=True)  # <== correct.env
        assert '128' == openhivenpy.env.env_vars['BOT_TOKEN_LEN']

    def test_load_false(self):
        _ = openhivenpy.env.load_env(path=self.FALSE_PATH, search_other=True)
        assert '132' == openhivenpy.env.env_vars['BOT_TOKEN_LEN']

        openhivenpy.env.load_env(path=self.FALSE_PATH,
                                 search_other=False)  # <== openhivenpy.env
        assert default_env_vars == openhivenpy.env.env_vars
        assert '132' == openhivenpy.env.env_vars['BOT_TOKEN_LEN']

        openhivenpy.env.unload_env()
        assert openhivenpy.env.load_env_file(path=self.FALSE_PATH)[1] is True

    def test_load_correct(self):
        assert openhivenpy.env.load_env_file(path=self.CORRECT_PATH)[1]  # <== correct.env

        openhivenpy.env.load_env(path=self.CORRECT_PATH, search_other=False)  # <== correct.env
        assert '128' == openhivenpy.env.env_vars['BOT_TOKEN_LEN']

        openhivenpy.env.load_env(path=self.CORRECT_PATH, search_other=True)  # <== correct.env
        assert '128' == openhivenpy.env.env_vars['BOT_TOKEN_LEN']
