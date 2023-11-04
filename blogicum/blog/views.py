from django.shortcuts import get_object_or_404, render

from blog.constants import POSTS_LIMIT
from blog.models import Category, Post


def index_view(request):
    template_name = 'blog/index.html'
    post_list = Post.filtered_objects.select_related(
        'category',
        'author',
        'location'
    ).order_by('-pub_date')[:POSTS_LIMIT]
    context = {
        'post_list': post_list}
    return render(request, template_name, context)


def post_detail_view(request, id):
    template_name = 'blog/detail.html'
    post_detail = get_object_or_404(
        Post.filtered_objects, pk=id)
    context = {'post': post_detail}
    return render(request, template_name, context)


def category_posts_view(request, category_slug):
    template_name = 'blog/category.html'
    title = 'Публикации в категории -'
    category_info = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug,
    )
    post_list = category_info.posts(manager='filtered_objects').select_related(
        'author',
        'location'
    ).order_by('-pub_date')
    context = {
        'title': title,
        'category': category_info,
        'post_list': post_list
    }
    return render(request, template_name, context)
