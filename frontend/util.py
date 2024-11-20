import asyncio
import websockets
import pyaudio
import threading
import logging
import json
import time
import struct

import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
VOLUME_REDUCTION_FACTOR = 0.6
# AUDIO_SERVER_URL = 'ws://localhost:5000/ws/akshat' # Your websocket URL
# Example: AUDIO_SERVER_URL = "ws://localhost:8080/ws/your_user_id"

async def audio_sender(Queues):
    queue =  Queues['rcv_aud']
    websocket = Queues['websocket']

    while True:

          audio_data = await queue.get()
          await websocket.send(audio_data)



def record_audio_to_queue(Queues, loop):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # print("Recording audio...")
    queue =  Queues['rcv_aud']
    
    try:
        while True:
            data = stream.read(CHUNK)
            asyncio.run_coroutine_threadsafe(queue.put(data), loop)
       
    except Exception as e:
        print(f"Error recording audio: {e}")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print('terminated')
        asyncio.run_coroutine_threadsafe(queue.put(None), loop)


async def receive_messages(Queues, eel):
        websocket = Queues['websocket']

        while True:
            message = await websocket.recv()
            print(f"Raw message: {message}")
            try:
                message = json.loads(message)
                if message.get('responseType') == 'user' or message.get('responseType') == 'assistant' or message.get('status') == 'error':
                    logging.info(message.get('text'))
                eel.receiveResponses(message)
            except Exception as e:
               print('error')
               eel.receiveResponses(message)
            except websockets.ConnectionClosed:
                print("Connection closed")
                eel.receiveResponses("Connection closed")
   

        

async def process_audio_in_queue(Queues, eel):

    try:    
        loop = asyncio.get_event_loop()
        audio_thread = threading.Thread(target=record_audio_to_queue, args=(Queues, loop))
        audio_thread.start()
        
        await asyncio.gather(
            audio_sender(Queues),
            receive_messages(Queues, eel)
        )
        loop.call_soon_threadsafe(loop.stop)
        loop.close()
    except Exception as e:
        print("Threading Stopped: ", e)

        # audio_thread.join()
