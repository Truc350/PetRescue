from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def get_home(request):
    return render(request, 'home.html')  # tra ve trang my_app trong trang web
def getChatWithAI(request):
    return render(request, 'fontend/chatWithAI.html')