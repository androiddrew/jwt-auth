import json
import unittest

from project.server import db
from project.server.models import User
from project.tests.base import BaseTestCase


class TestAuthBlueprint(BaseTestCase):

    def test_registraion(self):
        """Test for user registration"""
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_registered_with_already_registered_user(self):
        """Tests that the user registration resource returns 202"""
        user = User(
            email='joe@gmail.com',
            password='test'
        )
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='test'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(
                data['message'] == "User already exists. Please log in."
            )
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 202)

    def test_registered_user_login(self):
        """Test for login of registered user"""
        with self.client:
            register_response = self.client.post(
                '/auth/register',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json'
            )
            register_data = json.loads(register_response.data.decode())
            self.assertTrue(register_data['status'] == 'success')
            self.assertTrue(register_data['message'] == 'Successfully registered.')
            self.assertTrue(register_data['auth_token'])
            self.assertTrue(register_response.content_type == 'application/json')
            self.assertEqual(register_response.status_code, 201)
            # registered user login
            response = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_non_registered_user_login(self):
        """Test for login of a non-registered user"""
        response = self.client.post(
            '/auth/login',
            data=json.dumps(dict(
                email='notjoe@gmail.com',
                password='123456'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'failure')
        self.assertTrue(data['message'] == 'User does not exist.')
        self.assertTrue(response.content_type == 'application/json')
        self.assertEqual(response.status_code, 404)

    def test_user_registered_but_wrong_password(self):
        with self.client:
            register_response = self.client.post(
                '/auth/register',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json'
            )
            register_data = json.loads(register_response.data.decode())
            self.assertTrue(register_data['status'] == 'success')
            self.assertTrue(register_data['message'] == 'Successfully registered.')
            self.assertTrue(register_data['auth_token'])
            self.assertTrue(register_response.content_type == 'application/json')
            self.assertEqual(register_response.status_code, 201)
            # registered user login
            response = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='test'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(response['status'] == 'failure')
            self.assertTrue(response['message'] == 'Password provided was incorrect.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 401)

if __name__ == "__main__":
    unittest.main()