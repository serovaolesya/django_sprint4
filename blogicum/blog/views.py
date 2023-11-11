from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.constants import POSTS_LIMIT
from blog.models import Category, Comment, Post, User

from .forms import CommentForm, PostForm, UserForm


class PostModelMixin:
    model = Post
    paginate_by = POSTS_LIMIT


class PostFormMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class CommentFormMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'


class WhileUpdateDeleteMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", post_id=self.kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class PublishedPostsMixin:
    def get_published_posts_queryset(self):
        return Post.get_published_posts(self)


class AllPostsMixin:
    def get_all_posts_queryset(self):
        return Post.get_all_posts(self)


class Homepage(PostModelMixin, PublishedPostsMixin, ListView):
    template_name = 'blog/index.html'

    def get_queryset(self):
        return self.get_published_posts_queryset()


class UserInfoPage(PostModelMixin, AllPostsMixin,
                   PublishedPostsMixin, ListView):
    template_name = 'blog/profile.html'
    author = None

    def get_queryset(self):
        username = self.kwargs['username']
        self.author = get_object_or_404(User, username=username)
        if self.author == self.request.user:
            return self.get_all_posts_queryset().filter(author=self.author)
        return self.get_published_posts_queryset().filter(author=self.author)

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            profile=self.author
        )


class CreatePost(PostFormMixin, LoginRequiredMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostDetail(PostModelMixin, DetailView):
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    post = None

    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.post.author != self.request.user:
            if not (self.post.is_published and self.post.category.is_published
                    and self.post.pub_date <= timezone.now()):
                raise Http404('Публикация не найдена')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


class EditPost(PostFormMixin, WhileUpdateDeleteMixin,
               LoginRequiredMixin, UpdateView):
    pk_url_kwarg = 'post_id'


class LeaveComment(CommentFormMixin, LoginRequiredMixin, CreateView):
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


class EditComment(CommentFormMixin, WhileUpdateDeleteMixin,
                  LoginRequiredMixin, UpdateView):
    pk_url_kwarg = 'comment_id'


class DeleteComment(CommentFormMixin, WhileUpdateDeleteMixin,
                    LoginRequiredMixin, DeleteView):
    pk_url_kwarg = 'comment_id'


class CategoryPosts(PostModelMixin, PublishedPostsMixin, ListView):
    template_name = 'blog/category.html'
    category = None

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs["category_slug"],
            is_published=True,
        )
        return super().get_published_posts_queryset().filter(
            category=self.category
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class EditUserProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class DeletePost(PostFormMixin, LoginRequiredMixin, DeleteView):
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", post_id=self.kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)
