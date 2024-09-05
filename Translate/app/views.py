from django.shortcuts import render
from django.shortcuts import HttpResponse
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
from django.http import JsonResponse

load_dotenv()
groq_api_key = os.environ['groq_api_key']
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
# Create your views here.
def chatView(request):
    if request.method == "POST":
        message = request.POST.get('message')
        response = chatbot(message)
        response = emoji_pattern.sub(r'', response)
        return JsonResponse({"response": response})

    return render(request, "app/chat.html")