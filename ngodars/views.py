from django.shortcuts import render

# Create your views here.

def loading(request):
    return render(request, 'home/loading.html')

def index(request):
    return render(request, 'home/index.html')