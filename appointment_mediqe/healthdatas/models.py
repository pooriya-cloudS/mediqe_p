import uuid
from django.db import models
from accounts.models import User


# model of health data 
class HealthData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False, blank=False, editable=False, verbose_name="Health Data ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_data', verbose_name="User")
    ALLERGY = "Allergy"
    IMMUNIZATION = "Immunization"

    TYPE_CHOICES = [
        (ALLERGY, "Allergy"),
        (IMMUNIZATION, "Immunization"),
    ]

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=ALLERGY,
        verbose_name="Type of health data",
    )
    name = models.CharField(max_length=255, verbose_name="Name of the health data")
    reaction_or_provider = models.CharField(max_length=255, verbose_name="Reaction (for Allergy) or Provider (for Immunization)")
    severity_or_date = models.CharField(max_length=255, verbose_name="Severity (for Allergy) or Date (for Immunization)")

    class Meta:
        verbose_name = "Health Data"
        verbose_name_plural = "Health Data Records"
        ordering = ['-id']

    def __str__(self):
        return f"{self.type} - {self.name} for {self.user.username}"