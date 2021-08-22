# Quickstart

---

Welcome to the Quickstart page of OpenHiven.py!

OpenHiven.py is an easy tool for creating bots and utilising API Functionality of Hiven. Its goal is to be fast but also
provide good tools and functionality that can be used to write Hiven Bots easier. Therefore, OpenHiven.py is not a simple
API-Wrapper but adds nice features to make running a bot easier such as: 

* Data Caching for easier object fetching 
* Event listening using parallel execution and a MessageBroker to distribute processes for larger Bots
* WebSocket event and message handling for easier usage
* Usage of in-code event listeners to not be dependent on entire functions

!!! info

    The OpenHiven.py module is entirely written in async and can therefore only be used in an
    async event loop and environment. For more info about asyncio look into the [Asyncio documentation](https://docs.python.org/3/library/asyncio.html)

## Environment

OpenHiven.py is a Python module and can currently on be run in environments with Python >= 3.7. This is due to the used
module aiohttp which requires Functionality only available in Python 3.7 or higher! 

Python 2 is entirely not supported, and currently, there is no plan to make the module available for Python 2, since many 
features are dependent on Python 3 and the modern async module of Python 3 as well as aiohttp!

## Installation

OpenHiven.py can be easily installed using `pip`:

=== "PyPi Regular Installation"

    ```bash 
    python3 -m pip install -U openhivenpy
    ```

=== "PyPi Specific Version"

    ```bash 
    python3 -m pip install -U openhivenpy==version
    ```

=== "Github Build"
    
    !!! Warning
    
        Can be unstable due to development status! Only use if you need the most recent development version!

    ```bash
    python3 -m pip install -U https://github.com/Luna-Klatzer/OpenHiven.py/archive/main.zip
    ```

Installing OpenHiven.py will automatically also include its dependencies, which currently are:

* [aiohttp](https://docs.aiohttp.org/en/stable/) - *Async http client/server framework (asyncio)*

* [fastjsonschema](https://docs.python.org/3/library/asyncio.html) - *Fastest Python implementation of JSON schema*
  
* [yarl](https://docs.python.org/3/library/typing.html) - *Yet another URL library*

* [python-dotenv](https://docs.python.org/3/library/typing.html) - *Read key-value pairs from a .env file and set them as environment variable*

## Basic Concept

The system of OpenHiven.py is very closely related to the [discord.py](https://pypi.org/project/discord.py/) 
(Discord Python Wrapper) module and was structured to be similar to it. Therefore, the basic concept is based on an event 
listener system where events are mapped to user-specified functions and methods. These are user-declared and therefore
only what you specify will be executed and utilised, so the handling is up to you.

### The Hiven Swarm

The module uses a [aiohttp](https://docs.aiohttp.org/en/stable/) HTTP Websocket Connection to interact with the Hiven 
Swarm and react to events that the server sent over it. In case of an event, Hiven will send the corresponding data to 
you in the form of JSON-wrapped messages which gets automatically handled in OpenHiven.py. That means the library deals 
with events, keep-alive, close-frames and handling of the connection, and you only need to configure how to react. 
 
So, in this case, the Websocket will then pass the data to the EventHandler where the Hiven Swarm message will get processed, 
and an event would be triggered if the user declared it.

![OpenHiven.py System Visualised](../assets/images/openhivenpy-system.png)

### Event listening with the EventHandler 

The system used here is a classic event listening system where a client listens and waits over the connection for 
events and triggers specified code when the Websocket received such event. In Web-Languages such as JavaScript, TypeScript,
PHP etc. this is common practise and applied for websites, servers and clients. 

In Python, this is less common, so here it is not already integrated into the language, so OpenHiven.py uses aiohttp to
provide the option for a Connection to Hiven and its own [Event Handler](../reference/event_handler.html), 
which handles how the Client should react to such events.

**Now onto actual examples of how that works:**

To add an event listener, you must declare an async function with the correct name inside the HivenClient. 
This can be done either by inheriting the Client and then adding the method or using [decorators](https://realpython.com/primer-on-python-decorators/). 
Async Functions that are tagged with the `@client.event()` [decorator](https://realpython.com/primer-on-python-decorators/) 
will automatically be registered in the EventHandler and then called whenever an Event is triggered.
    
!!! note

    All events that can you can use are listed on the page for the 
    [EventHandler](../getting_started/event_handling.html).

Example with the event `on_message_create`:

```python
import openhivenpy as hiven

client = hiven.UserClient(token="")

@client.event()
async def on_message_create(msg):
    print(f"{msg.author.name} send a message: {msg.content}")

...
```

## Using OpenHiven.py

### Using a UserClient
[:octicons-file-code-24: Source Code · `openhivenpy.UserClient`](https://github.com/Luna-Klatzer/openhiven.py/blob/main/openhivenpy/client/userclient.py)

A UserClient object is an object that wraps the default [HivenClient](../reference/hivenclient.html),
which serves as a bridge between Hiven, and the Program you are using.

The [HivenClient](../reference/hivenclient.html) contains all data and 
connection-vital information, but is not supposed to be used directly since
some methods are not available due to the raw state. These are special methods 
related to the bot-type that decides based on what type you are using, 
resulting in various functionality. These two bot-types are here 
[UserClient](../reference/userclient.html) and [BotClient](../reference/botclient.html).

For the usage of a HivenClient, you are required to pass your token, which it will use to authorise on Hiven 
and request data. If no token was passed, it will automatically raise an `openhivenpy.exceptions.exception.InvalidToken`
Exception!

!!! note "Usage Examples"

    === "Regular"

        Note that using a decorator will also automatically add the function as a method to the [Event Handler](https://openhivenpy.readthedocs.io/en/latest/)
        instance itself so it can call it directly from the Event Handler and it doesn't need to reference the origin!

        ```python
        
        import openhivenpy as hiven
        
        client = hiven.UserClient("Insert token")
        
        @client.event()
        async def on_ready():
            print("Bot is ready")

        client.run()
        
        ```

    === "Inherited"

        Decorators are useful for beginners and for a quick setup, but it is recommended to use a class which 
        inherits the HivenClient, making the Event listener directly find the methods when needed without needing 
        the methods to be registered.

        This can save time as well as remove unneeded logic

        ```python
        import openhivenpy as hiven
        
        class Bot(hiven.UserClient):
            def __init__(self, token):
                self._token = token
                # Calling __init__ of the parent class and inheriting all methods and functionality
                super().__init__(token)
        
            # Not directly needed but protects the token from ever being changed!
            @property
            def token(self):
                return self._token
        
            # Methods can be defined directly in the class 
            async def on_ready(self):
                print("Bot is ready!")
        
        
        if __name__ == '__main__':
            client = Bot(token="Insert token")
            client.run()
        ```

### Using a BotClient
[:octicons-file-code-24: Source Code · `openhivenpy.BotClient`](https://github.com/Luna-Klatzer/openhiven.py/blob/main/openhivenpy/client/botclient.py)

A Bot Client like the UserClient is a wrapper for the main HivenClient class. It serves as a Class using bot
functionality on Hiven. Therefore, it's usage is very similar to the UserClient, but it can specifically utilise Methods 
and functions related to text-commands and will likely receive in future versions more updates specifically adding that 
functionality.

!!! Warning
    **The current release v0.1.3.2 the BotClient lacks major optimisation and functionality. 
    Therefore, bugs are likely to occur! If you encounter such bugs, please report them!**


## Hiven-Types
[:octicons-file-code-24: Source Code · `openhivenpy.types`](https://github.com/Luna-Klatzer/openhiven.py/blob/main/openhivenpy/types/)

You might have already noticed in prior examples that instead of raw data OpenHiven.py sends entire instances of Classes 
with the event data as parameters. This is because of the type-system OpenHiven.py uses where objects are created and 
initialised parallel to the corresponding Hiven ones, making it easier for usage due to the easy attribute
and data access of a Python class.

These instances can then be used through methods to interact with the Hiven API directly, instead of you having to write 
your own requests for fetching the data and having to update the objects accordingly yourself.

For each possible request OpenHiven.py already ships a pre-made method to the 
class which automatically changes data and returns configured objects if that specific methods returns data.

For detailed documentation see [Data Models](https://openhivenpy.readthedocs.io/en/latest/)
