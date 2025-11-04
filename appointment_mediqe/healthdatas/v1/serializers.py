# healthdatas/serializers.py
from rest_framework import serializers
from ..models import HealthData
from accounts.permissions import user_is_admin

class HealthDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthData
        fields = ['id', 'user', 'type', 'name', 'reaction_or_provider', 'severity_or_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def validate(self, attrs):
        """Validate logical consistency based on type."""
        data_type = attrs.get('type') or getattr(self.instance, 'type', None)
        if data_type == HealthData.ALLERGY and not attrs.get('reaction_or_provider'):
            raise serializers.ValidationError("Allergy entries must include a reaction.")
        if data_type == HealthData.IMMUNIZATION and not attrs.get('severity_or_date'):
            raise serializers.ValidationError("Immunization entries must include a date.")
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        if user_is_admin(user):
            # Admin can create for any user (if user provided)
            return HealthData.objects.create(**validated_data)
        # Normal users always create for themselves
        validated_data['user'] = user
        return HealthData.objects.create(**validated_data)
