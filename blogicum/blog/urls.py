from django.urls import path

from . import views

app_name = 'blog'


urlpatterns = [
    path('', views.index_view, name='index'),
    path('posts/<int:id>/', views.post_detail_view, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts_view,
         name='category_posts'),
]
