from django.contrib import admin

from .models import *


admin.site.empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    ordering = ('title',)
    list_per_page = 10
    inlines = (
        PostInline,
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 10
    inlines = (
        PostInline,
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'location',
        'is_published',
        'pub_date',
        'created_at'
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = (
        'title',
        'author',
        'location',
    )
    list_filter = ('category', 'author', 'location')
    list_display_links = ('title',)
    ordering = ('pub_date',)
    list_per_page = 10
