from django.shortcuts import render
from django.shortcuts import HttpResponse
from .chatbot import Chatwithgroq


def chatView(request):
    if request.method == "POST":
        message = request.POST.get('message')
        response = Chatwithgroq(message)

    return render(request, "app/chat.html")