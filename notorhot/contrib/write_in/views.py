from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.
class WriteInDefaultView(TemplateView):
    def dispatch(self, request):
        return HttpResponse('it lives!')