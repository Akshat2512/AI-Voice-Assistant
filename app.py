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
  
    websocket = await websockets.connect('ws://localhost:5000/ws/'+user_id)
    print('Websocket connected established')
    if not user_id in Queues:
        Queues[user_id] = {}
        Queues[user_id]['rcv_aud'] = asyncio.Queue()
        Queues[user_id]['websocket'] = websocket
        Queues[user_id]['signal'] = signal
    


        asyncio.create_task(process_audio_in_queue(Queues[user_id], eel))
    
    # task = asyncio.create_task()
    # await task



eel.init('frontend')

 # Start Eel with the main HTML file 
eel.start('index.html', block=False, port=8000) 

while True:
    eel.sleep(1.0)   