import os
import numpy as np
from groq import Groq
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
import re
from django.http import JsonResponse


# Configurations
load_dotenv()
groq_api_key = os.environ['groq_api_key']


# Chat with LLM
def chatbot(user_input):

    llm=ChatGroq( groq_api_key=groq_api_key,model_name="Gemma2-9b-It",max_tokens=100)

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


## Emoji
emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  
                           u"\U0001F300-\U0001F5FF"  
                           u"\U0001F680-\U0001F6FF"  
                           u"\U0001F700-\U0001F77F"  
                           u"\U0001F780-\U0001F7FF"  
                           u"\U0001F800-\U0001F8FF"  
                           u"\U0001F900-\U0001F9FF" 
                           u"\U0001FA00-\U0001FA6F"  
                           u"\U0001FA70-\U0001FAFF"  
                           u"\U00002700-\U000027BF"  
                           u"\U0001F1E0-\U0001F1FF"  
                           u"\U00002500-\U00002BEF"  
                           u"\U000024C2-\U0001F251"  
                           "]+", flags=re.UNICODE)

# Main
def Chatwithgroq(text):
    response = chatbot(text)
    response = emoji_pattern.sub(r'', response)
    response = JsonResponse({"response": response})
    return response