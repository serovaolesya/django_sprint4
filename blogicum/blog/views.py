from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.constants import POSTS_LIMIT
from blog.models import Category, Comment, Post, User

from .forms import CommentForm, PostForm, UserForm


class PrePublishedMixin:
    def get_queryset(self):
        queryset = Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')
        return queryset


class Homepage(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_LIMIT
    queryset = Post.filtered_objects.select_related(
        'category',
        'author',
        'location').annotate(
            comment_count=Count('comment')).order_by('-pub_date')


class UserInfoPage(ListView):
    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = POSTS_LIMIT
    author = None

    def get_queryset(self):
        username = self.kwargs['username']
        self.author = get_object_or_404(User, username=username)
        if self.author == self.request.user:
            return Post.objects.select_related(
                'category',
                'author',
                'location').order_by(
                '-pub_date'
            ).annotate(comment_count=Count('comment')
                       ).filter(author=self.author)
        return Post.filtered_objects.select_related(
            'category',
            'author',
            'location').annotate(comment_count=Count('comment')
                       ).order_by('-pub_date').filter(author=self.author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class CreatePost(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostDetail(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    ordering = ("-pub_date",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if post.author != self.request.user:
            if not (post.is_published and post.category.is_published
                    and post.pub_date <= timezone.now()):
                raise Http404('Публикация не найдена')

        context['form'] = CommentForm()
        context['comments'] = self.object.comment.all()
        return context

def post_detail_view(request, id):
    template_name = 'blog/detail.html'
    post_detail = get_object_or_404(
        Post.filtered_objects, pk=id)
    context = {'post': post_detail}
    return render(request, template_name, context)


class EditPost(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", post_id=self.kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class LeaveComment(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    post_comment = None

    def dispatch(self, request, *args, **kwargs):
        self.post_comment = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_comment
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class EditComment(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", post_id=self.kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class DeleteComment(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", post_id=self.kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class PrePublishedMixin:
    def get_queryset(self):
        queryset = Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')
        return queryset


class CategoryPosts(PrePublishedMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'
    category = None
    paginate_by = 10

    def get_queryset(self):
        slug = self.kwargs["category_slug"]
        self.category = get_object_or_404(
            Category, slug=slug, is_published=True,
        )
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context

    #     context['title'] = PostForm(instance=self.object)
    #     return context


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


class EditUserProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class DeletePost(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", post_id=self.kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    # def dispatch(self, request, *args, **kwargs):
    #     get_object_or_404(Post, pk=kwargs['post_id'], author=request.user)
    #     return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)



