
from django.shortcuts import render


def home(request):
    return render(request, "home.html")
def user_manual(request):
    return render(request, "user_manual.html")
def about_us(request):
    return render(request, "about_us.html")



