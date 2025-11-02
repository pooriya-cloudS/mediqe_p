from django.contrib import admin
from .models import HealthData

# Register your models here.


@admin.register(HealthData)
class HealthDataAdmin(admin.ModelAdmin):
    pass