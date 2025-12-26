from django.urls import path
from . import views

app_name = 'blog'


def url_with_names(path_str, view_class, *names):
    """Создает несколько URL с разными именами для одной view."""
    patterns = []
    for name in names:
        patterns.append(path(path_str, view_class.as_view(), name=name))
    return patterns


urlpatterns = [
    # Главная страница
    path('', views.IndexView.as_view(), name='index'),

    # Категории
    path(
        'category/<slug:category_slug>/',
        views.CategoryView.as_view(),
        name='category_posts'
    ),
    path(
        'categories/<slug:category_slug>/',
        views.CategoryView.as_view(),
        name='category'
    ),

    # Посты
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),

    # Создание поста
    *url_with_names(
        'posts/create/',
        views.PostCreateView,
        'post_create',
        'create_post'
    ),

    # Редактирование поста
    *url_with_names(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView,
        'post_edit',
        'edit_post'
    ),

    # Удаление поста
    *url_with_names(
        'posts/<int:post_id>/delete/',
        views.PostDeleteView,
        'delete_post'
    ),

    # Комментарии
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),

    # Пользователи
    path(
        'auth/registration/',
        views.RegistrationView.as_view(),
        name='registration'
    ),
    path(
        'profile/<str:username>/',
        views.ProfileView.as_view(),
        name='profile'
    ),
    path(
        'profile/<str:username>/edit/',
        views.ProfileEditView.as_view(),
        name='profile_edit'
    ),
]
