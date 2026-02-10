from django.contrib import admin
from .models import BusinessDefinition, Employee, Task

admin.site.register(BusinessDefinition)
admin.site.register(Employee)
admin.site.register(Task)
