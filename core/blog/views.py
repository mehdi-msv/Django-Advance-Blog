from django.shortcuts import render ,redirect
from django.views.generic import TemplateView , RedirectView , ListView , DetailView , FormView , CreateView , UpdateView , DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from .models import Post
from accounts.models import Profile
from .forms import ContactForm , PostForm
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
    '''

    '''
    url = 'https://www.djangoproject.com/'
    
    def get_redirect_url(self, *args, **kwargs):
        post = Post.objects.get(pk=kwargs['pk'])
        print(post)
        return super().get_redirect_url(*args, **kwargs)

class PostListView(PermissionRequiredMixin,ListView):
    '''
    This is a class-based view to show list of posts.
    '''
    permission_required = "blog.view_post"
#    model = Post
    queryset = Post.objects.filter(status=True)
    context_object_name = 'posts'
    ordering = '-published_date'
    paginate_by = 2
    # def get_queryset(self):
    #     posts = Post.objects.filter(status=True)
    #     return posts
        
class PostDetailView(LoginRequiredMixin,DetailView):
    '''
    This is a class-based view to show detail page of a post.
    '''
    model = Post
    context_object_name = 'post' # for using post instead of object in template
#   template_name = 'blog/post_detail.html'
class ContactView(FormView):
    '''
    This is a class-based view to show contact form.
    '''
    template_name = 'blog/contact_us.html'
    form_class = ContactForm
    success_url = '/blog/posts/'
 
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        return super(ContactView, self).form_valid(form)

class PostCreateView(LoginRequiredMixin,CreateView):
    '''
    This is a class-based view to create a new post.
    '''
    model = Post
#   fields = ['title', 'content', 'category', 'status', 'published_date'] ##can use it instead of form_class
    form_class = PostForm
    success_url = '/blog/posts/'
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.instance.author = Profile.objects.get(user=self.request.user)
        print(type(Profile.objects.get(user=self.request.user)),type(self.request.user))
        return super(PostCreateView, self).form_valid(form)
    
class PostEditView(LoginRequiredMixin,UpdateView):
    '''
    This is a class-based view to edit an existing post.
    '''
    model = Post
    form_class = PostForm
    success_url = '/blog/posts'

class PostDeleteView(LoginRequiredMixin,DeleteView):
    '''
    This is a class-based view to delete an existing post.
    '''
    model = Post
    success_url = '/blog/posts/'
    