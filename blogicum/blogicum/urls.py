from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler403, handler404, handler500

# Обработчики ошибок - из приложения pages
handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),  # Все URL блога
    path('pages/', include('pages.urls')),  # Статичные страницы
    path('auth/', include('django.contrib.auth.urls')),  # Авторизация Django
]
