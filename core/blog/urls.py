from django.urls import path,include
from django.views.generic.base import RedirectView
from . import views

app_name = 'blog'

urlpatterns = [
    path('fbv-index', views.fbv_index, name='fbv_index'),
#    path('cbv-index', TemplateView.as_view(template_name='index.html', extra_context={'name':'mehdi'}),name='cbv_index'),
    path('cbv-index', views.IndexView.as_view(), name='cbv_index'),
    path(
        "go-to-django/",
        RedirectView.as_view(url="https://www.djangoproject.com/"),
        name="go-to-django",
    ),
    path(
        'go-to-index',
         RedirectView.as_view(pattern_name='blog:cbv_index'),
         name='go-to-index'
         ),
    
]
