from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ..pagination import HealthDataPagination
from ..models import HealthData
from .serializers import HealthDataSerializer
from accounts.permissions import UniversalPermissionMixin, filter_queryset_by_role


class HealthDataViewSet(UniversalPermissionMixin, viewsets.ModelViewSet):
    """
    Manage user health data (Allergies & Immunizations).
    - Admins: full access (any user)
    - Users: access only their own entries
    """
    serializer_class = HealthDataSerializer
    queryset = HealthData.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = HealthDataPagination

    # get the permission of the user
    def get_permissions(self):
        return self.get_universal_permissions({
            'list': ['Admin', 'Patient'],
            'retrieve': ['Admin', 'Patient'],
            'create': ['Admin', 'Patient'],
            'update': ['Admin', 'Patient'],
            'partial_update': ['Admin', 'Patient'],
            'destroy': ['Admin', 'Patient'],
        })

    # get the querysets based on the type and user role
    def get_queryset(self):
        queryset = filter_queryset_by_role(
            HealthData.objects.all(),
            self.request.user,
            {
                'Patient': {'user': self.request.user},
                'Admin': {}
            }
        )
        data_type = self.request.query_params.get('type')
        if data_type in [HealthData.ALLERGY, HealthData.IMMUNIZATION]:
            queryset = queryset.filter(type=data_type)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        data_user = self.request.data.get('user')

        if hasattr(user, 'role') and user.role == 'Admin' and data_user:
            serializer.save(user_id=data_user)
        else:
            serializer.save(user=user)

    # ✅ Document query params for GET /api/v1/health/healthdatas/
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='type',
                description='Filter health data by type (Allergy or Immunization)',
                required=False,
                type=str,
                enum=[HealthData.ALLERGY, HealthData.IMMUNIZATION],
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """List all health data (Admins) or user’s own (Patients)."""
        return super().list(request, *args, **kwargs)

    # ✅ Document query params for GET /api/v1/health/healthdatas/{id}/
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='type',
                description='Optional filter: ensure the record matches the given type (Allergy or Immunization)',
                required=False,
                type=str,
                enum=[HealthData.ALLERGY, HealthData.IMMUNIZATION],
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve specific health data (Admins can access any, Patients only their own)."""
        return super().retrieve(request, *args, **kwargs)
