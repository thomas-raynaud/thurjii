from django.shortcuts import render
from django.http import HttpResponse

from .models import Parcelle

# Create your views here.
def parcelles(request):
    return HttpResponse("Parcelles...")