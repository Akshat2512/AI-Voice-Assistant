import eel
import asyncio
import websockets
from frontend.util import process_audio_in_queue



Queues = {}   

@eel.expose
def handle_connect(user_id, signal):

    print('Client connected')
 
    asyncio.run(handle_async_connect(user_id, signal))

async def handle_async_connect(user_id, signal): 
  
    websocket = await websockets.connect('ws://localhost:5001/ws/'+user_id)
    print('Websocket connection established')
    Queues['user_id'] = user_id
    Queues['rcv_aud'] = asyncio.Queue()
    Queues['websocket'] = websocket
    Queues['signal'] = signal

    asyncio.gather (
            await process_audio_in_queue(Queues, eel)
    )

    

eel.init('frontend')

 # Start Eel with the main HTML file 
eel.start('index.html', block=False, port=8000) 

while True:
    eel.sleep(1.0)   