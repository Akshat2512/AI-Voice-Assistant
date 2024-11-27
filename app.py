from fastapi import WebSocket, FastAPI, Request
import numpy as np
from fastapi.templating import Jinja2Templates 
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import HTMLResponse
import io

import uvicorn

from backend.speech_proccessing import process_audio_stream
from backend.openai_models import transcribe_audio, generate_response, generate_image_response, ChatHistory

import time, wave
import asyncio
import json
import os
from datetime import datetime


import logging
logger = logging.getLogger("uvicorn")

# from dotenv import load_dotenv # Load environment variables from .env file 

# load_dotenv()

app = FastAPI()

users_directory = {}    # maintain users database or their chat history in their where each key represents the user_id

app.mount("/static", StaticFiles(directory="static"), name="static") 
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse) 
async def get(request: Request): 
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket('/ws/{user_id}')     # will be responsible for handling real time stream of audio chunks and all AI generated responses will be sent to the streamer client 
async def chat(websocket: WebSocket, user_id: str):
    i = 0
    if user_id not in users_directory: 
        users_directory[user_id] = ChatHistory()   # creates an instance of the ChatHistory class and each user will have their own instance of ChatHistory

    chat_history = users_directory[user_id]
    
    await websocket.accept()
 
    audio_queue = asyncio.Queue()
    response_queue = asyncio.Queue()

    process_task = asyncio.create_task(process_audio_stream(audio_queue, response_queue))   # It will create asynchrounous task to handle audio_queue in the background, detect speeches in the audio_queue using pre trained Model and add it to response_queue
   
    while True:
        
        try:
            result = await handle_audio_new(websocket, audio_queue)
            logger.info('%d', i)
            i = i + 1
            if not result:
                print('Stopping background process')
                process_task.cancel()
                break

            
            # await audio_queue.put(result)
            # print(audio_queue.qsize())
            if not response_queue.empty():
              logger.info('Speech detected')
              await generate_ai_response(response_queue, websocket, user_id, chat_history)   #  for generating ai responses and send it back to the client

            
            if not websocket.application_state.CONNECTED:
                break

            # await websocket.send_text(result)
         
        except Exception as e:
          
            # print(f"Connection error: {e}")
            await websocket.send_text('connection_closed')
            await websocket.close()
        
   

async def handle_audio_new(websocket: WebSocket, audio_queue):  
    
    try:
        audio_data = await websocket.receive_bytes()   # receives the audio stream from clients
        kolkata_time = datetime.now() # Print the current time 
        await websocket.send_json({"Recieved":kolkata_time.strftime('%Y-%m-%d %H:%M:%S')})

        with wave.open(io.BytesIO(audio_data), 'rb') as wav_file:
            # print(wav_file.getframerate(), wav_file.getsampwidth(), wav_file.getnchannels(), wav_file.getnframes())
           
            while True:
                audio_data = wav_file.readframes(1024)
        
                if not audio_data:
                    break
                await audio_queue.put(audio_data)      

        return True
    except Exception as e:
        print(e)
        print("Websocket gets Disconnected")
        return False
        
    


async def generate_ai_response(response_queue, websocket, user_id, chat_history):        
      
               audio_path = "backend/temp/"
               if not os.path.exists(audio_path):
                  os.makedirs(audio_path)

               audio_data = await response_queue.get()
               result = save_audio_to_file(audio_data, audio_path+f'recording_{user_id}.wav')

               if result == 'file saved':
                  prompt = transcribe_audio(audio_path+f'recording_{user_id}.wav', os.getenv('OPENAI_API_KEY'))  # generate texts from audio using whisper-1 model
                  
                  if len(prompt) >= 2:
                   
                    logger.info('Transcribing: %s', prompt)

                    message = {"responseType" : "user", "text" : prompt[:-1]}
                    # message = json.dumps(message)
                    await websocket.send_json(message)
                    
                    
                    response = generate_response(prompt, os.getenv('OPENAI_API_KEY'), chat_history)  # generate natural language using gpt-4o model  
                    await asyncio.sleep(0.1)
                    
                    if "CALL DALL-E" == response:
                        message = {"responseType" : "assistant", "text": response}
                        # message = json.dumps(message)
                        await websocket.send_json(message)
                        await asyncio.sleep(0.1)

                        print('Generating Image ...')
                    
                        image = generate_image_response(prompt, os.getenv('OPENAI_API_KEY')) # generate image from text using DALL-E-3 model
                           
                        try:
                            message = {"responseType" : "assistant", "revised_prompt":image.revised_prompt, "image_url": image.url}
                        except Exception as e:
                            await websocket.send_json('{"status": "error"}')

                        # message = json.dumps(message)
                        await websocket.send_json(message)
                        # print(message)
                    else:
                        message = {"responseType" : "assistant", "text" : response}
                        # message = json.dumps(message)
                        await websocket.send_json(message)

                    logger.info('GPT-4o AI: %s', response)



def save_audio_to_file(audio_data, file_path):    # save audio to the folder temporary.
       CHANNELS=1
       sample_width = 2
       RATE = 16000
       num_samples = len(audio_data) // sample_width 
       original_duration = num_samples / RATE
       min_duration = 0.1

    #    print(original_duration)
       if(original_duration > min_duration):
         with wave.open(file_path, 'wb') as wav_file:
           wav_file.setnchannels(CHANNELS)  # Mono audio
           wav_file.setsampwidth(sample_width)  # 16-bit audio
           wav_file.setframerate(RATE)  # Sample rate
          
           wav_file.writeframes(audio_data) # save file to folder
           return 'file saved'
      
           return 'file saved'
       else:
          return 'file is short'
  

# if __name__ == '__main__':
#    uvicorn.run(app, host='0.0.0.0', port=5000)
# #    uvicorn.run(app, host='localhost', port=5000)

   