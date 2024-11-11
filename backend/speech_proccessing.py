import pyaudio
# import wave
import numpy as np
import tensorflow as tf
import zipfile
import time

# Audio stream configuration
FORMAT = pyaudio.paInt16  # 16-bit PCM
CHANNELS = 1  # Mono channel
RATE = 16000  # 16kHz sample rate
CHUNK = 1024  # Buffer size
TARGET_LENGTH = 15600


model_path = 'backend/model/1.tflite'
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

waveform_input_index = input_details[0]['index']
scores_output_index = output_details[0]['index']


with zipfile.ZipFile(model_path) as z:
    with z.open('yamnet_label_list.txt') as f:
        labels = [line.decode('utf-8').strip() for line in f]

# Ensure the input tensor is correctly sized
interpreter.resize_tensor_input(waveform_input_index, [TARGET_LENGTH], strict=False)
interpreter.allocate_tensors()
# Initialize PyAudio
# p = pyaudio.PyAudio()
   
# stream = p.open(format=FORMAT,
#                         channels=CHANNELS,
#                         rate=RATE,
#                         input=True,
#                         frames_per_buffer=CHUNK)

async def check_mic_output(audio_queue, response_queue):
    audio_buffer = np.zeros(TARGET_LENGTH, dtype=np.float32)
    audio_chunks = []
    try:
       
        # Open the audio stream
        
        # print("Listening... Press Ctrl+C to stop.")

        flag = 0
        silence = 0
        # Continuously read from the stream and append to audio_data
  
        while True:
            
            # audio_data = stream.read(CHUNK)
            # print(aud_data)
            audio_data = await audio_queue.get()
            
            audio_chunk = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                    # audio_chunk_hey_ova = np.frombuffer(audio_data, dtype=np.int16)
            audio_buffer = np.roll(audio_buffer, -len(audio_chunk))
            audio_buffer[-len(audio_chunk):] = audio_chunk

            # Set the tensor data
            interpreter.set_tensor(waveform_input_index, audio_buffer)

            # Run the model
            interpreter.invoke()
            scores = interpreter.get_tensor(scores_output_index)
        
            # Get the top classification result
            top_class_index = scores.argmax()
            prediction = labels[top_class_index]
            # await response_queue.put(prediction)
            # print(response_queue.qsize())
            
            if( prediction == 'Speech' or prediction == 'Whispering'):
                audio_chunks.append(audio_data)
                # await response_queue.put(audio_data)
                flag = flag+1
                # silence = 0
                # i=5
            elif(flag < 10 and prediction !='Speech' and prediction !='Whispering'):
                silence = silence+1

            elif(flag >= 10  and prediction !='Speech' and prediction !='Whispering'):
                audio_data = b''.join(audio_chunks)
                await response_queue.put(audio_data)
                audio_chunks = []
                silence = 0
                flag = 0

            
            if(silence == 5):
                audio_chunks = []
                silence = 0
                flag = 0

    except Exception as e:
        # Handle the KeyboardInterrupt to stop recording
        print(e)

    # finally:
    #     # Stop and close the stream and terminate PyAudio
    #     stream.stop_stream()
    #     stream.close()
    #     p.terminate()
    #     print("Stream closed and resources released.")



# check_mic_output(None)