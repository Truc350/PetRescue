from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import json
from accounts.models import UserProfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def trangChinhSachVanChuyen(request):
    return render(request, 'frontend/ChinhSachVanChuyen.html')

def trangChinhSachDoiTraHang(request):
    return render(request, 'frontend/ChinhSachDoiTraHang.html')

def trangLienHe(request):
    return render(request, 'frontend/LienHe.html')

def trangThanhToanTienLoi(request):
    return render(request, 'frontend/ThanhToanTienLoi.html')

