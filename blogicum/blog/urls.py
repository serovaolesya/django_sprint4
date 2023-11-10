from django.urls import path

from . import views

app_name = 'blog'


urlpatterns = [
    path('', views.Homepage.as_view(), name='index'),
    path('edit_profile/', views.EditUserProfile.as_view(),
         name='edit_profile'),
    path('profile/<slug:username>/', views.UserInfoPage.as_view(),
         name='profile'),
    path('posts/create/', views.CreatePost.as_view(), name='create_post'),
    path('posts/<int:post_id>/', views.PostDetail.as_view(),
         name='post_detail'),
    path('posts/<int:post_id>/edit/', views.EditPost.as_view(),
         name='edit_post'),
    path('posts/<int:post_id>/delete/', views.DeletePost.as_view(),
         name='delete_post'),
    path('posts/<int:post_id>/comment/', views.LeaveComment.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.EditComment.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.DeleteComment.as_view(), name='delete_comment'),
    path('category/<slug:category_slug>/', views.CategoryPosts.as_view(),
         name='category_posts'),
]
