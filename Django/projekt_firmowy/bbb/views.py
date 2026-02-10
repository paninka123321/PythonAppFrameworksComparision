from rest_framework import viewsets, permissions
from .models import Task, User
from .serializers import TaskSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.models import User


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

class CurrentUserView(APIView):
    def get(self, request):
        return Response({
            "username": request.user.username,
            "is_admin": request.user.groups.filter(name='Managerowie').exists()
        })
    
# fetch users
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

def users_tasks_view(request):
    # Pobieramy wszystkich userów
    # Używamy prefetch_related('tasks'), żeby Django nie robiło 100 zapytań do bazy (optymalizacja)
    users = User.objects.prefetch_related('tasks').all()
    
    context = {
        'users': users
    }
    return render(request, 'users_tasks.html', context)