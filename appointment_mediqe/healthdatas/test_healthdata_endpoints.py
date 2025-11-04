from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import HealthData
from accounts.models import User


class HealthDataAPITest(TestCase):
    """Test suite for HealthData endpoints using phone as main user field."""

    def setUp(self):
        self.client = APIClient()

        # Create users using 'phone' instead of 'email'
        self.patient_user = User.objects.create_user(
            phone="09121234567",
            password="patientpass",
            role="Patient",
        )
        self.admin_user = User.objects.create_user(
            phone="09129876543",
            password="adminpass",
            role="Admin",
            is_staff=True,
        )
        # Create initial health data for patient
        self.health_data = HealthData.objects.create(
            user=self.patient_user,
            type=HealthData.ALLERGY,
            name="Pollen Allergy",
            reaction_or_provider="Sneezing",
            severity_or_date="Severe",
        )

        self.list_url = reverse("healthdata-list")
        self.detail_url = reverse("healthdata-detail", args=[self.health_data.id])

    # ---------------- AUTHENTICATION TESTS ---------------- #

    def test_list_healthdata_authenticated_patient(self):
        """Authenticated patient should see only their own health data."""
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data["results"]) >= 1)
        self.assertEqual(str(response.data["results"][0]["user"]), str(self.patient_user.id))


    def test_list_healthdata_authenticated_admin(self):
        """Admin should see all health data."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data["results"]) >= 1)

    def test_list_healthdata_unauthenticated_user(self):
        """Unauthenticated user should not access health data list."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------- RETRIEVE TESTS ---------------- #

    def test_retrieve_healthdata_as_patient(self):
        """Patient can retrieve their own health data."""
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.health_data.id))

    def test_retrieve_healthdata_as_admin(self):
        """Admin can retrieve any user's health data."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_healthdata_unauthenticated(self):
        """Unauthenticated user should not retrieve data."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------- CREATE TESTS ---------------- #

    def test_create_healthdata_as_patient(self):
        """Patient can create their own health data."""
        self.client.force_authenticate(user=self.patient_user)
        data = {
            "type": HealthData.IMMUNIZATION,
            "name": "Flu Shot",
            "reaction_or_provider": "City Clinic",
            "severity_or_date": "1403-07-10",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_healthdata_as_admin_for_user(self):
        """Admin can create health data for any user."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "user": str(self.patient_user.id),
            "type": HealthData.IMMUNIZATION,
            "name": "COVID Vaccine",
            "reaction_or_provider": "Tehran Hospital",
            "severity_or_date": "1403-02-15",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_healthdata_unauthenticated(self):
        """Unauthenticated user should be denied create access."""
        data = {
            "type": HealthData.ALLERGY,
            "name": "Dust",
            "reaction_or_provider": "Coughing",
            "severity_or_date": "Mild",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------- PAGINATION TEST ---------------- #

    def test_pagination_on_large_dataset(self):
        """If user has more than 10 health data, pagination should appear."""
        self.client.force_authenticate(user=self.patient_user)
        for i in range(15):
            HealthData.objects.create(
                user=self.patient_user,
                type=HealthData.ALLERGY,
                name=f"Test Allergy {i}",
                reaction_or_provider="Cough",
                severity_or_date="Mild",
            )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("next", response.data)
        self.assertIsNotNone(response.data["next"])  # Next page should exist
