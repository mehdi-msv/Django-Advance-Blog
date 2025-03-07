from django.urls import path,include
from django.views.generic import TemplateView
from .views import fbv_index

urlpatterns = [
    path('fbv-index', fbv_index, name='fbv_index'),
    path('cbv-index', TemplateView.as_view(template_name='index.html', extra_context={'name':'mehdi'}),name='cbv_index'),
]
