from rest_framework import viewsets, permissions
from .models import Task, User
from .serializers import TaskSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

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