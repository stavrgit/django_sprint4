from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, UpdateView, DetailView, ListView, DeleteView
)
from .models import Post, Category, Comment
from django.shortcuts import get_object_or_404
from django.http import Http404


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    ordering = ['-pub_date']

    def get_queryset(self):
        from django.utils import timezone
        queryset = Post.objects.filter(
            is_published=True,
            category__isnull=False,
            pub_date__lte=timezone.now()
        ).select_related('category', 'author',
                         'location').prefetch_related('comments')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for post in context['object_list']:
            post.comment_count_repr = f"({post.comments.count()})"
        return context


class CategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        from django.utils import timezone

        category = get_object_or_404(Category,
                                     slug=self.kwargs['category_slug'])
        return category.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug']
        )
        return context


# blog/views.py
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post_id = self.kwargs['post_id']

        # Пытаемся получить опубликованный пост
        try:
            post = Post.published.get(id=post_id)
        except Post.DoesNotExist:
            # Если пост не опубликован, проверяем доступ для автора
            try:
                post = Post.objects.get(id=post_id)
                if self.request.user != post.author:
                    raise Http404("Пост не найден")
            except Post.DoesNotExist:
                raise Http404("Пост не найден")

        return post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    fields = ['title', 'text', 'image', 'category', 'location', 'pub_date']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    fields = ['title', 'text', 'image', 'category', 'location', 'pub_date']
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('blog:post_detail', post_id=obj.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.id})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('blog:post_detail', post_id=obj.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


# КОММЕНТАРИИ
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['text']

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['text']
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('blog:post_detail', post_id=obj.post.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.post.id})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('blog:post_detail', post_id=obj.post.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.post.id})


# ПОЛЬЗОВАТЕЛИ
class RegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        if self.request.user == user:
            posts = user.posts.all()
        else:
            posts = user.posts.filter(is_published=True)

        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        for post in page_obj:
            post.comment_count_repr = f"({post.comments.count()})"

        context['posts'] = page_obj
        context['page_obj'] = page_obj
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/profile_edit.html'
    fields = ['first_name', 'last_name', 'username', 'email']

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})
