from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardViewTests(TestCase):
    def test_passenger_dashboard_is_public(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'passenger_dashboard.html')

    def test_admin_dashboard_requires_login(self):
        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 302)

    def test_admin_dashboard_renders_for_staff(self):
        user = get_user_model().objects.create_user(username='dispatcher', password='secret1234')

        self.client.force_login(user)
        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertTrue(response.context['is_admin'])

    def test_welcome_page_renders(self):
        response = self.client.get(reverse('welcome'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'welcome.html')


class LiveTrackingViewTests(TestCase):
    def test_bus_map_is_public(self):
        response = self.client.get(reverse('bus:bus_map'))

        self.assertEqual(response.status_code, 200)
