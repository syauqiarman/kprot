from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Selamat datang, {user.username}!")
            return redirect("testapp:list_semester")  # Ganti dengan halaman setelah login
        else:
            messages.error(request, "Username atau password salah!")

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Anda telah logout!")
    return redirect("login:login")  # Redirect ke halaman login
