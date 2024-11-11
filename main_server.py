from fastapi import APIRouter, WebSocket, FastAPI
import uvicorn

from backend.speech_proccessing import check_mic_output
from backend.openai_models import transcribe_audio, generate_response, generate_image_response, ChatHistory
import time, wave
import asyncio
import json
import os

app = FastAPI()

users_directory = {}    # maintain users database or their chat history in their 
chat_history = ChatHistory()    # creates an instance of the ChatHistory class and each user will have their own instance of ChatHistory



@app.websocket('/ws/{user_id}')     # will be responsible for handling real time or contiguous stream of audio chunks and then from here all AI response will be sent to specific client 
async def chat(websocket: WebSocket, user_id: str):

    if user_id not in users_directory: 
        users_directory[user_id] = ChatHistory()

    chat_history = users_directory[user_id]
    await websocket.accept()
    audio_queue = asyncio.Queue()
    response_queue = asyncio.Queue()

    process_task = asyncio.create_task(check_mic_output(audio_queue, response_queue))
    
    while True:
        message=''
        try:
            result = await handle_audio_new(websocket)
    
            await audio_queue.put(result)
            # print(response_queue.qsize())
           
            
            if not response_queue.empty():
               
               audio_path = "backend/temp/"
               if not os.path.exists(audio_path):
                  os.makedirs(audio_path)

               audio_data = await response_queue.get()
               response = await save_audio_to_file(audio_data, audio_path+'recording.wav')

               if response == 'file saved':
                  prompt = transcribe_audio(audio_path+'recording.wav', os.getenv('OPENAI_API_KEY'))
                  
                  if len(prompt) >= 2:
                   
                    print('Transcribing: ', prompt)

                    message = {"responseType" : "user", "text" : prompt[:-1]}
                    message = json.dumps(message)
                    await websocket.send_text(message)
                                                
                    result = generate_response(prompt, os.getenv('OPENAI_API_KEY'), chat_history)
                 
                    if "Generating image ..." in result:
                    
                        image = generate_image_response(prompt, os.getenv('OPENAI_API_KEY'))
                        print(image)
                        try:
                         message = {"responseType" : "assistant", "text":result, "revised_prompt":image.revised_prompt, "image_url": image.url}
                        except Exception as e:
                          await websocket.send_text(image)

                        message = json.dumps(message)
                        await websocket.send_text(message)
                        # print(message)
                    else:
                        message = {"responseType" : "assistant", "text" : result}
                        message = json.dumps(message)
                        await websocket.send_text(message)

                    print('GPT-4o AI: ', result, "\n")

            if not websocket.application_state.CONNECTED:
                break

     
            # await websocket.send_text(result)
         
        except Exception as e:
            time.sleep(1)
            await websocket.close()
            # print(f"Connection error: {e}")
            await websocket.send_text('connection_closed')

async def handle_audio_new(websocket: WebSocket):    # receives the audio stream from clients
    audio_data = await websocket.receive_bytes()
    return audio_data

async def save_audio_to_file(audio_data, file_path):    # save audio to the folder temporary, it is not user specific yet.
       CHANNELS=1
       sample_width = 2
       RATE = 16000
       num_samples = len(audio_data) // sample_width 
       original_duration = num_samples / RATE
       min_duration = 0.1
       if(original_duration > min_duration):
         with wave.open(file_path, 'wb') as wav_file:
           wav_file.setnchannels(CHANNELS)  # Mono audio
           wav_file.setsampwidth(sample_width)  # 16-bit audio
           wav_file.setframerate(RATE)  # Sample rate
           # save file to folder
           wav_file.writeframes(audio_data)
           return 'file saved'
       else:
          return 'file is short'
  

if __name__ == '__main__':
   uvicorn.run(app, host='localhost', port=5000)