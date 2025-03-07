from django.urls import path,include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('fbv-index', views.fbv_index, name='fbv_index'),
#    path('cbv-index', TemplateView.as_view(template_name='index.html', extra_context={'name':'mehdi'}),name='cbv_index'),
    path('cbv-index', views.IndexView.as_view(), name='cbv_index'),
]
