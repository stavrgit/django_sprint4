from django.contrib import admin
from .models import Category, Location, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'description')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'pub_date',
        'category',
        'location',
        'is_published',
        'created_at'
    )
    list_editable = ('is_published', 'category', 'location')
    list_filter = ('is_published', 'category', 'location', 'pub_date')
    search_fields = ('title', 'text')
    list_display_links = ('title', 'author')

    # Для удобного редактирования даты публикации
    date_hierarchy = 'pub_date'

    # Поля в форме редактирования
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'text', 'image', 'author')
        }),
        ('Дополнительно', {
            'fields': ('category', 'location', 'pub_date', 'is_published')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'text_preview')
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'author__username', 'post__title')
    list_display_links = ('author', 'post')

    def text_preview(self, obj):
        """Короткий предпросмотр текста комментария"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'
