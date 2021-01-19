import openhivenpy as hiven
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    client = hiven.UserClient(token="Insert token here")
    client.run()
