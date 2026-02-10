from rest_framework import serializers
from .models import Task
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(many=True, read_only=True)
    assigned_to_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=User.objects.all(), source="assigned_to", required=False
    )

    class Meta:
        model = Task
        fields = ["id", "title", "description", "due_date", "assigned_to", "assigned_to_ids", "status"]

    def validate_assigned_to_ids(self, value):
        user = self.context['request'].user
        
        # ZMIANA: Tutaj też wpisujemy 'Managerowie'
        is_manager = user.groups.filter(name='Managerowie').exists()

        if value and not is_manager:
            raise serializers.ValidationError(
                "Brak uprawnień. Tylko członkowie grupy 'Managerowie' mogą przydzielać zadania."
            )
            
        return value