from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Expense(models.Model):
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE)
