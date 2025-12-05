import os
from openai import OpenAI
from together import Together
import time
import base64

from dotenv import load_dotenv # Load environment variables from .env file 

load_dotenv()

class ChatHistory:
    def __init__(self):
        self.process_lists = []
        self.messages = [
                            {
                                "role": "system",
                                "content": "You are a helpful assistant."
                            }
                        ]

        self.tools = [
            {
                "type": "function",
                "function": {
                "name": "generate_image",
                "description": "Generate an image based on users text, if user ask for image generation."
                }
            }
            ]

    def add_user_message(self, prompt):
        self.messages.append({
            "role": "user",
            "content": prompt
        })

    def add_assistant_message(self, prompt):
        self.messages.append({
            "role": "assistant",
            "content": prompt
        })

gen_client = OpenAI(api_key = os.getenv("GEMINI_API_KEY"), base_url = os.getenv("GEMINI_BASE_URL"))

async def transcribe_audio( websocket, audio_file):  # Transcribe audio file using Gemini 2.0 flash model
    
    base64_audio = base64.b64encode(audio_file.read()).decode('utf-8')

    try:
                       
            response = gen_client.chat.completions.create(
                    model="gemini-2.0-flash",
                    messages=[
                        {
                        "role": "user",
                        "content": [
                            {
                            "type": "text",
                            "text": "Transcribe the following audio. Do not describe its sounds or context, just provide the transcript of spoken words.",
                            },
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": base64_audio,
                                    "format": "wav"
                            }
                            }
                        ]
                        }
                    ],
                )
            
            result = response.choices[0].message.content
                # print(response.text)
            # await websocket.send_json({"Type":"transcribed_text","id": rel_id, "message": {"id": 0, "responder":"User", "message": response.choices[0].message.content, "time": current }})
            return result
    except Exception as e:
            print(f"Error during transcription: {e}")
            await websocket.send_json({"Type": "Transcription error"})
            return None
                     

    
    
async def generate_response(prompt, chat_history, index, websocket):  # Generate response from user's text using OpenAI's GPT-4o model 
    chat_history.process_lists.append(True)
    print(chat_history.process_lists)
    assistant_response = ""
    # client = OpenAI(api_key=API_KEY)
    await websocket.send_json({"responseType": "assistant", "text": "<stream>"})
    try:
        # Add the user's message to the history
        chat_history.add_user_message(prompt)
        
                     
        response = gen_client.chat.completions.create(
                    model="gemini-2.0-flash",
                    messages=chat_history.messages,
                    tools=chat_history.tools,
                    tool_choice="auto",
                    stream=True
                )
            

        for chunk in response:
            time.sleep(0.01)
            # assistant_response = response.choices[0].message.content
            # chat_history.add_assistant_message(assistant_response)
            
            if chat_history.process_lists[index] == False:
              chat_history.add_assistant_message(assistant_response)
              await websocket.send_json({"Type": "assistant", "stream": "</stream>"})
              return
            content = chunk.choices[0].delta.content or ""
            
            tool_call = chunk.choices[0].delta.tool_calls
            if(tool_call and tool_call[0].function.name == "generate_image"):
                    message = {"responseType" : "assistant", "text": "<FLUX-1>"}
                    # message = json.dumps(message)
                    await websocket.send_json(message)

                    print('Generating Image ...')
                
                    image = generate_image_response(prompt) # generate image from text using DALL-E-3 model
                        
                    try:
                        message = {"responseType" : "assistant", "revised_prompt":"Here, is your image", "image_url": image.url}
                    except Exception as e:
                        await websocket.send_json({"status": "error"})
                        return False
                    # message = json.dumps(message)
                    await websocket.send_json(message) 
            # pipe.append(content) 
            await websocket.send_json({"responseType": "assistant", "text": content})
            assistant_response = assistant_response + content
            # print(content, end="", flush=True)
        
        chat_history.process_lists[index] = False
        await websocket.send_json({"responseType": "assistant", "text": "</stream>"})
        chat_history.add_assistant_message(assistant_response)
  

                # logger.info('GPT-4o AI: %s', response)

    except Exception as e:
        return str(e)


client = Together(api_key=os.getenv("META_API_KEY"))
def generate_image_response(prompt):  # Generate image from text using DALL-E-3 model

    # client = OpenAI(api_key=API_KEY)

    try:
        response = client.images.generate(
            model="black-forest-labs/FLUX.1-schnell-Free",
            prompt=prompt,
            steps=4,
            size="1024x1024",
            quality="standard",
            n=1
        )
        result = response.data[0]
        print(response.data)
        return result

    except Exception as e:
        print(e)
        return str(e)


# def generate_image(prompt):
        
#     response = client.images.generate(
#         model="imagen-3.0-generate-002",
#         prompt="a portrait of a sheepadoodle wearing a cape",
#         response_format='b64_json',
#         n=1,
#     )

#     for image_data in response.data:
#      image = Image.open(BytesIO(base64.b64decode(image_data.b64_json)))
#     image.show()
