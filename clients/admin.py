from django.contrib import admin
from .models import ClientProfile

# Register your models here.
@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth', 'height', 'current_weight', 'goal_weight', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('created_at', 'updated_at')
