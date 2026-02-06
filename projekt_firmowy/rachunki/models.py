from django.db import models

class Bill(models.Model):
    YEAR_CHOICES = [(2025, '2025')]

    year = models.IntegerField(choices=YEAR_CHOICES)
    month = models.IntegerField()
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.category} - {self.month}/{self.year}"
    