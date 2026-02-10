from django.db import models
from django.contrib.auth.models import User

class BusinessDefinition(models.Model):
    term = models.CharField(max_length=200)
    definition = models.TextField()

    def __str__(self):
        return self.term


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Task(models.Model):
    # Defining statuses for the Kanban board
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_process', 'In Process'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ManyToManyField(User, related_name="tasks", blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    def __str__(self):
        return self.title
