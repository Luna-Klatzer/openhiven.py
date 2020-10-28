import openhivenpy
import asyncio

# Simple test to get a simple response from the Hiven API
client = openhivenpy.UserClient(token="TOKEN", heartbeat=1)
response = asyncio.run(client.get())

# If response is 200 that means the program can interact with Hiven
if response.status_code == 200:
    print("Success")
else:
    print(f"The process failed. STATUSCODE={response.status_code}")

# Starts the Event loop with the a specified websocket => can also be a different websocket
asyncio.run(client.start_event_loop(websocket=client.websocket))

