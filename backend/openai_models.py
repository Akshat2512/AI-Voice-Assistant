import os
from openai import OpenAI
# import openai
from pathlib import Path

class ChatHistory:
    def __init__(self):
        self.messages = [
                            {
                                "role": "system",
                                "content": "You are a helpful assistant."
                            },
                            {
                                "role": "system",
                                "content":  "Please avoid using text surrounded by asterisks in your responses."
                            },
                            {
                                "role": "system",
                                "content":  "Always only write exactly this keyword \"CALL DALL-E\" in your responses when user intent is to generate an image."
                            },
                            { 
                               "role": "system",
                               "content": " When user intent to know the owner or developer of this assistant?' always respond that 'Akshat Gangwar' is the developer who created you as an AI Assistant. Feel free to phrase it differently each time."
                            }

                        #  {
                        #     "role": "system",
                        #     "content": "You are a helpful assistant and always reply only with these keywords when user intent is to generate an image \"CALL DALL-E\"" 
                        #  },
                        #  { 
                        #     "role": "system",
                        #     "content": "When someone asks, 'Who is your owner?' or 'Who made you?', always respond that 'Akshat Gangwar' is the developer who created you as an AI Assistant. Feel free to phrase it differently each time."
                        #  }
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

def transcribe_audio(audio_file_path, API_KEY):  # Transcribe audio file using OpenAI's Whisper-1 model

    client = OpenAI(api_key=API_KEY)
    
    try:
        # Open the audio file
        audio_file = Path(audio_file_path)
        
        with open(audio_file, "rb") as audio:
            # Send to Whisper API
            transcript = client.audio.transcriptions.create(
                model="whisper-1",  # Current model version
                file=audio,
                language="en",
                response_format="text"  # Can also be: json, srt, verbose_json, or vtt
            )
        
        return transcript
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None
    
    finally: 
        # Clean up the temporary file 
        if os.path.exists(audio_file_path): 
            os.remove(audio_file_path)


def generate_response(prompt, API_KEY, chat_history):  # Generate response from user's text using OpenAI's GPT-4o model 

    client = OpenAI(api_key=API_KEY, base_url="https://api.pawan.krd/cosmosrp/v1/")
    
    try:
        # Add the user's message to the history
        chat_history.add_user_message(prompt)

        response = client.chat.completions.create(
            model="gpt-4o",
            # model="gpt-3.5-turbo",
            messages=chat_history.messages
        )

        # Get the assistant's response and add it to the history
        assistant_response = response.choices[0].message.content
        chat_history.add_assistant_message(assistant_response)
    
        return assistant_response

    except Exception as e:
        return str(e)


def generate_image_response(prompt, API_KEY):  # Generate image from text using DALL-E-3 model

    client = OpenAI(api_key=API_KEY)

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0]
        print(response.data)
        return image_url

    except Exception as e:
        return str(e)






# # Example usage
# if __name__ == "__main__":
#     user_prompt = "Tell me a joke about artificial intelligence."
#     generated_text = generate_response(user_prompt)
#     print("Generated Response:", generated_text)
