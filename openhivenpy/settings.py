def load_env():
    from dotenv import load_dotenv, find_dotenv

    # Loading the .env data
    load_dotenv(find_dotenv())
