def load_env():
    from dotenv import load_dotenv, find_dotenv

    # Fetching the paths origin and finding the openhivenpy.env file
    load_dotenv(f"{__file__}\\..\\openhivenpy.env")
