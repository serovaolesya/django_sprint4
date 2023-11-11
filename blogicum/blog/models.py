from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.utils import timezone

from core.models import PublishedModel

User = get_user_model()


class PublishedPostsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,)


class Category(PublishedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        max_length=64,
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL;'
                  ' разрешены символы латиницы,'
                  ' цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем'
                  ' — можно делать отложенные публикации.')
    image = models.ImageField('Изображение',
                              upload_to=settings.POST_IMAGES_UPLOAD_FOLDER,
                              blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )
    objects = models.Manager()
    filtered_objects = PublishedPostsManager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def get_published_posts(self):
        return Post.filtered_objects.select_related(
            'category',
            'author',
            'location'
        ).annotate(comment_count=Count(
            'comments'
        )).order_by('-pub_date')

    def get_all_posts(self):
        return Post.objects.select_related(
            'category',
            'author',
            'location'
        ).annotate(comment_count=Count(
            'comments'
        )).order_by('-pub_date')

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация',

    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Добавлено")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор',)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at', ]

    def __str__(self):
        return self.text
