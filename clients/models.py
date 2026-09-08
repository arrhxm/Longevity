from django.conf import settings
from django.db import models

# Create your models here.
class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='client_profile')
    phone=models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    goal_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    health_goals = models.TextField(blank=True)
    medical_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    