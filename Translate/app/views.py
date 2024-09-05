from django.shortcuts import render
from django.shortcuts import HttpResponse

# Create your views here.
def chatView(request):
    if request.method == "POST":
        message = request.POST.get('message')
        print(message)
    return render(request, "app/chat.html")