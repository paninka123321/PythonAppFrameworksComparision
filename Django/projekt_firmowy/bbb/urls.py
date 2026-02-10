# bbb/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CurrentUserView, UserViewSet, users_tasks_view  # <--- Dodaj import users_tasks_view

# Routery dla API (jeśli masz je tu zdefiniowane, zostaw bez zmian)
router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    # ... Twoje stare ścieżki API ...
    path('', include(router.urls)),
    
    # --- NOWA ŚCIEŻKA DLA PANELU HTML ---
    # To sprawi, że pod adresem /staff/tasks/ zobaczysz swoją tabelkę
    path('staff/tasks/', users_tasks_view, name='users_tasks_list'),
]