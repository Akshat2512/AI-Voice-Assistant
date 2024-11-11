import os
from openai import OpenAI
from pathlib import Path


# Set your OpenAI API key
class ChatHistory:
    def __init__(self):
        self.messages = [{
                            "role": "system",
                            "content": "You are a helpful assistant and always exactly say \"Generating image ...\" when user ask to generate image" 
                         }]

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

def transcribe_audio(audio_file_path, API_KEY):  # Transcribe audio file using OpenAI's Whisper model

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


    client = OpenAI(api_key=API_KEY)

    try:
        # Add the user's message to the history
        chat_history.add_user_message(prompt)

        response = client.chat.completions.create(
            model="gpt-4o",
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
        return image_url

    except Exception as e:
        return str(e)






# # Example usage
# if __name__ == "__main__":
#     user_prompt = "Tell me a joke about artificial intelligence."
#     generated_text = generate_response(user_prompt)
#     print("Generated Response:", generated_text)
