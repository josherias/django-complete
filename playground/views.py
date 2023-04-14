from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product
from django.contrib.contenttypes.models import ContentType
from tags.models import TaggedItem



def say_hello(request):
    TaggedItem.objects.get_tags_for(Product, 1)
        
    return render(request, 'hello.html', {'name': 'Josh'})
