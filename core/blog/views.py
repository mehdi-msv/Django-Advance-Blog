from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Post
# Create your views here.
def fbv_index(request):
    context = {'name':'mehdi'}
    return render(request, 'index.html',context)

class IndexView(TemplateView):
    '''
    This is a class-based view for index page
    '''
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = 'mehdi'
        context['posts'] = Post.objects.all()
        return context