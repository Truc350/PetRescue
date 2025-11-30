from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def get_home(request):
    return render(request, 'home.html')  # tra ve trang my_app trong trang web
def getChatWithAI(request):
    return render(request, 'fontend/chatWithAI.html')
def getFooter(request):
    return render(request, 'fontend/footer.html')
def getHeader(request):
    return render(request, 'fontend/header.html')
def getLogin(request):
    return render(request, 'fontend/login.html')
def getRegister(request):
    return render(request, 'fontend/register.html')
def getForgotPassword(request):
    return render(request, 'fontend/forgot-password.html')