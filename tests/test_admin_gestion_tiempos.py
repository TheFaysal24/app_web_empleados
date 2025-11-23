import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from flask_testing import TestCase
from flask_login import login_user, logout_user

class AdminGestionTiemposTest(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def login_as_user(self, user):
        with self.client:
            login_user(user)

    def logout(self):
        with self.client:
            logout_user()

    def test_access_denied_for_non_admin(self):
        with self.client:
            class DummyUser:
                def __init__(self):
                    self.admin = False
                    self._id = "dummy_user_id"
                    self._username = "dummy_username"
                    self._nombre = "Dummy User"
                def is_active(self):
                    return True

                def is_authenticated(self):
                    return True

                def get_id(self):
                    return self._id
                def is_admin(self):
                    return False
                @property
                def id(self):
                    return self._id
                @property
                def username(self):
                    return self._username
                @property
                def nombre(self):
                    return self._nombre

            login_user(DummyUser())
            response = self.client.get('/admin/gestion_tiempos', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.request.path.endswith('/dashboard') or response.request.path.endswith('/login'))
            logout_user()

    def test_admin_gestion_tiempos_page(self):
        with self.client:
            class DummyAdminUser:
                def __init__(self):
                    self.admin = True
                    self._username = "dummy_admin_username"
                    self._nombre = "Dummy Admin"
                def is_active(self):
                    return True

                def is_authenticated(self):
                    return True

                def get_id(self):
                    return "dummy_admin_user_id"
                @property
                def username(self):
                    return self._username
                def is_admin(self):
                    return True
                @property
                def id(self):
                    return "dummy_admin_user_id"
                @property
                def nombre(self):
                    return self._nombre

            login_user(DummyAdminUser())
            response = self.client.get('/admin/gestion_tiempos')
            self.assertIn(response.status_code, (200, 302))
            self.assert_template_used('admin_gestion_tiempos.html')
            self.assertIn('Resumen Uso de Turnos'.encode('utf-8'), response.data)
            self.assertIn('Grafico horas extras diarios'.encode('utf-8'), response.data or b'')
            logout_user()

    def test_page_parameters(self):
        with self.client:
            class DummyAdminUser:
                def __init__(self):
                    self.admin = True
                    self._username = "dummy_admin_username"
                    self._nombre = "Dummy Admin"
                def is_active(self):
                    return True

                def is_authenticated(self):
                    return True

                def get_id(self):
                    return "dummy_admin_user_id"
                @property
                def username(self):
                    return self._username
                def is_admin(self):
                    return True
                @property
                def id(self):
                    return "dummy_admin_user_id"
                @property
                def nombre(self):
                    return self._nombre

            login_user(DummyAdminUser())
            response = self.client.get('/admin/gestion_tiempos?mes=1&ano=2024')
            self.assertIn(response.status_code, (200, 302))
            self.assert_template_used('admin_gestion_tiempos.html')
            self.assertIn('Resumen Uso de Turnos'.encode('utf-8'), response.data)
            logout_user()

if __name__ == '__main__':
    unittest.main()
