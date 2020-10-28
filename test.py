import openhivenpy
import asyncio

# Simple test to get a simple response from the Hiven API
client = openhivenpy.HivenClient(client_type="user")
response = asyncio.run(client.get())

if response.status_code == 200:
    print("Success")
else:
    print(f"The process failed. STATUSCODE={response.status_code}")
