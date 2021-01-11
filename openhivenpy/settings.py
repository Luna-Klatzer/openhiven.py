def load_env():
    from dotenv import load_dotenv, find_dotenv

    # Loading the openhivenpy.env data
    load_dotenv(find_dotenv("openhivenpy.env"))
