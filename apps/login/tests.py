import smtplib
from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class PasswordResetTests(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='reset_user',
            email='reset_user@example.com',
            password='TempPass123!',
        )

    def test_password_reset_redirects_when_email_sends(self):
        response = self.client.post(
            reverse('account_reset_password'),
            {'email': 'reset_user@example.com'},
            secure=True,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('account_reset_password_done'))

    @patch('allauth.account.forms.ResetPasswordForm.save', side_effect=smtplib.SMTPException('smtp down'))
    def test_password_reset_shows_error_when_email_fails(self, _):
        response = self.client.post(
            reverse('account_reset_password'),
            {'email': 'reset_user@example.com'},
            secure=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No pudimos enviar el correo de restablecimiento en este momento.',
        )

    @patch(
        'allauth.account.adapter.get_current_site',
        side_effect=Site.DoesNotExist,
    )
    def test_password_reset_shows_error_when_site_missing(self, _):
        response = self.client.post(
            reverse('account_reset_password'),
            {'email': 'reset_user@example.com'},
            secure=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'La recuperación de contraseña no está configurada correctamente en el servidor.',
        )
