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
        # data = stream.read(CHUNK)
        # print(queue.qsize())
          audio_data = await queue.get()
          await websocket.send(audio_data)

        # exit(0)
        

def record_audio_to_queue(Queues, loop):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # print("Recording audio...")
    queue =  Queues['rcv_aud']
    websocket = Queues['websocket']
    try:
        while True:
            data = stream.read(CHUNK)
            # Convert data to numpy array 
            # audio_data = np.frombuffer(data, dtype=np.int16) 
            # Reduce volume 
            # reduced_audio_data = (audio_data * VOLUME_REDUCTION_FACTOR).astype(np.int16) # Convert numpy array back to bytes
            # data = reduced_audio_data.tobytes()
             
            asyncio.run_coroutine_threadsafe(queue.put(data), loop)
            # loop.call_soon_threadsafe(loop.stop)
            # break

    except Exception as e:
        print(f"Error recording audio: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    
        asyncio.run_coroutine_threadsafe(queue.put(None), loop)
        # loop.call_soon_threadsafe(loop.stop)
        # loop.close()

async def receive_messages(Queues, eel):
        websocket = Queues['websocket']

        while True:
            message = await websocket.recv()
            # print(f"Raw message: {message}")
            try:
                message = json.loads(message)
                if message.get('responseType') == 'user' or message.get('responseType') == 'assistant':
                    logging.info(message.get('text'))
                eel.receiveResponses(message)
            except Exception as e:
               eel.receiveResponses(message)
            except websockets.ConnectionClosed:
                print("Connection closed")
                eel.receiveResponses("Connection closed")
            # elif message.get('chatType' == 'gpt_response'):
            #     logging.info(message.get('text'))
            # logging.info(message)
            
    # except websockets.ConnectionClosed:
    #     print("Connection closed")
    #     eel.receiveResponses("Connection closed")
    # except Exception as e:
    #     print(f"Error receiving message: {e}")
        

async def process_audio_in_queue(Queues, eel):
# async def main():

    # async with websockets.connect(AUDIO_SERVER_URL) as websocket:
        # queue = asyncio.Queue()
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

# if __name__ == "__main__":
#     asyncio.run(main())