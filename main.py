#https://www.koyeb.com/tutorials/using-groq-to-build-a-real-time-language-translation-app


import os
import sounddevice as sd
import numpy as np
import wave
import keyboard
from groq import Groq
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
import pyttsx3
import pvorca
import time
import winsound
import re



# API Keys
load_dotenv()
groq_api_key = os.environ['groq_api_key']
ACCESS_KEY = os.environ['PVORCA']



# Configurations
orca = pvorca.create(access_key=ACCESS_KEY)
client = Groq()
sample_rate = 44100
channels = 2
output_filename = 'recorded_audio.wav'


# Function to record audio
def record_audio():
    print("Press 'Space' to start and stop recording.")
    recording = False
    audio_frames = []

    def callback(indata, frames, time, status):
        if recording:
            audio_frames.append(indata.copy())

    stream = sd.InputStream(samplerate=sample_rate, channels=channels, callback=callback, dtype='int16')

    with stream:
        while True:
            if keyboard.is_pressed('space'):
                if not recording:
                    print("Recording started...")
                    recording = True
                    audio_frames.clear()
                else:
                    print("Recording stopped.")
                    recording = False
                    break
            sd.sleep(100)  

    # Save the recorded audio
    audio_data = np.concatenate(audio_frames)
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    return output_filename


# Function to convert recorded audio to text using the provided API
def text_converted(audio_file):
    with open(audio_file, 'rb') as file:
        translation = client.audio.translations.create(
            file=(audio_file, file.read()),
            model="whisper-large-v3",
            prompt="Specify context or spelling",
            response_format="json",
            temperature=0.0
        )
    return translation.text


# LLM interaction function
def chatbot(user_input):

    llm=ChatGroq(groq_api_key=groq_api_key,model_name="Gemma2-9b-It",max_tokens=100)

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    graph_builder = StateGraph(State)

    def chatbot(state: State):
        return {"messages": llm.invoke(state['messages'])}

    graph_builder.add_node("Chatbot", chatbot)
    graph_builder.add_edge(START, "Chatbot")
    graph_builder.add_edge("Chatbot", END)
    graph = graph_builder.compile()

    for event in graph.stream({'messages':("user",user_input)}):
        print("Human: ",user_input)
        for value in event.values():
            return value["messages"].content

emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # Emoticons
                           u"\U0001F300-\U0001F5FF"  # Miscellaneous Symbols and Pictographs
                           u"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
                           u"\U0001F700-\U0001F77F"  # Alchemical Symbols
                           u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                           u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           u"\U00002700-\U000027BF"  # Dingbats
                           u"\U0001F1E0-\U0001F1FF"  # Flags (iOS)
                           u"\U00002500-\U00002BEF"  # Other miscellaneous symbols
                           u"\U000024C2-\U0001F251"  # Enclosed characters
                           "]+", flags=re.UNICODE)

if __name__ == '__main__':
    try:
        while True:
            recorded_file = record_audio()
            print("Processing your message... Please wait")
            text = text_converted(recorded_file)

            # Interact with Chatbot
            response = chatbot(text)
            response = emoji_pattern.sub(r'', response)
            pcm, alignments = orca.synthesize(text=response)
            alignments = orca.synthesize_to_file(text=response,output_path='tranlate.wav')
            print("Chatbot:", response)
            winsound.PlaySound("tranlate.wav", winsound.SND_FILENAME) 


    except Exception as e:
        print(e)
