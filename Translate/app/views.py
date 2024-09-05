from django.shortcuts import render
from django.shortcuts import HttpResponse

# Create your views here.
def chatView(request):
    return render(request, "app/chat.html")