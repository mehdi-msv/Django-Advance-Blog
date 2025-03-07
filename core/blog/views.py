from django.shortcuts import render

# Create your views here.
def fbv_index(request):
    context = {'name':'mehdi'}
    return render(request, 'index.html',context)
    