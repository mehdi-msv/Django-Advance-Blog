from django.shortcuts import render ,redirect
from django.views.generic import TemplateView , RedirectView , ListView
from .models import Post
# Create your views here.

# Function-based view to show index page
'''
def fbv_index(request):
    """
    This is a function-based view to show index page
    """
    context = {'name':'mehdi'}
    return render(request, 'index.html',context)
'''
# Redirecting to Django's official website with Function-based view
'''
def redirect_to_django(request, *args, **kwargs):
    post = Post.objects.get(pk=kwargs['pk'])
    print(post)
    return redirect('https://www.djangoproject.com')
'''
class IndexView(TemplateView):
    '''
    This is a class-based view to show index page
    '''
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = 'mehdi'
        context['posts'] = Post.objects.all()
        return context
    
class RedirectToDjango(RedirectView):
    url = 'https://www.djangoproject.com/'
    
    def get_redirect_url(self, *args, **kwargs):
        post = Post.objects.get(pk=kwargs['pk'])
        print(post)
        return super().get_redirect_url(*args, **kwargs)

class PostList(ListView):
    '''
    
    '''
#    model = Post
#    queryset = Post.objects.filter(status=True)
    context_object_name = 'posts'
    def get_queryset(self):
        posts = Post.objects.filter(status=True)
        return posts
    