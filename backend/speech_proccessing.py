
# import wave
import numpy as np
# import tensorflow.lite as tflite
import zipfile
import time
import tflite_runtime.interpreter as tflite

import logging

logger = logging.getLogger("uvicorn")  # Using the current module's name

TARGET_LENGTH = 15600

model_path = "backend/model/1.tflite"
interpreter = tflite.Interpreter(model_path)

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


async def process_audio_stream(audio_queue, response_queue):
    audio_buffer = np.zeros(TARGET_LENGTH, dtype=np.float32)
    audio_chunks = []
    audio_data = b''
    i = 0
        # Open the audio stream
        
        # print("Listening... Press Ctrl+C to stop.")

    speak = 0
    silence = 0
        # Continuously read from the stream and append to audio_data
  
    while True:
          try: 
            audio_data = await audio_queue.get()
            
            audio_chunk = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
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
            # print(prediction, len(audio_data) )
            i = i + 1
            logger.info("%s, %d", prediction, len(audio_data), i)

            if( prediction == 'Speech'):
                audio_chunks.append(audio_data)
                # await response_queue.put(audio_data)
                speak = speak+1
                # silence = 0
                # i=5
            elif(speak < 10 and prediction !='Speech'):
                silence = silence+1

            elif(speak >= 10  and prediction !='Speech'):
                audio_data = b''.join(audio_chunks)
                await response_queue.put(audio_data)
                audio_chunks = []
                silence = 0
                speak = 0

            
            if(silence == 5):
                audio_chunks = []
                silence = 0
                speak = 0

          except Exception as e:
                # print(audio_data)
                print(e)

