from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from testapp.models import *


def temp_logout(request):
    logout(request)
    return redirect('login:login')
