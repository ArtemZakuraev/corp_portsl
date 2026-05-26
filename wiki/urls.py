"""Wiki app URLs."""
from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    path('', views.article_list, name='list'),
    path('<slug:slug>/', views.article_detail, name='detail'),
    path('create/', views.create_article, name='create'),
    path('<slug:slug>/edit/', views.edit_article, name='edit'),
    path('<slug:slug>/upload/', views.upload_attachment, name='upload_attachment'),
]
