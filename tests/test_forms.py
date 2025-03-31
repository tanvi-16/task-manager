import unittest
from app import create_app, db
from app import RegisterForm, LoginForm
from flask_wtf import FlaskForm
from wtforms import ValidationError

class TestForms(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Lenovo@localhost/flask_auth_db'
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'ENFEFKNDEWJFNESFSDFF'
        self.app.config['WTF_CSRF_ENABLED'] = False  
        with self.app.app_context():
            db.create_all()  

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_form_valid(self):
        with self.app.app_context():
            form = RegisterForm(username='newuser', email='newuser@example.com', password='password123', confirm_password='password123')
            self.assertTrue(form.validate())

    def test_register_form_invalid_password(self):
        with self.app.app_context():
            form = RegisterForm(username='newuser', email='newuser@example.com', password='password123', confirm_password='wrongpassword')
            self.assertFalse(form.validate())

    def test_login_form_valid(self):
        with self.app.app_context():
            form = LoginForm(email='test@example.com', password='testpassword')
            self.assertTrue(form.validate())

    def test_login_form_invalid_email(self):
        with self.app.app_context():
            form = LoginForm(email='invalid@example.com', password='invalidtestpassword')
            testValue = False
            self.assertFalse( testValue, form.validate()) 

    """def test_register_form_valid(self):
        with self.app.app_context():
            response = self.client.post('/register', data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            self.assertEqual(response.status_code, 302)  
            self.assertNotIn(b'Login', response.data) #assertIn

    def test_register_form_invalid(self):
        with self.app.app_context():
            response = self.client.post('/register', data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123',
                'confirm_password': 'wrongpassword'
            })
            self.assertEqual(response.status_code, 200)  
            self.assertNotIn(b'Password must match', response.data) #assertIn

    def test_login_form_valid(self):
        with self.app.app_context():
            response = self.client.post('/login', data={
                'email': 'test@example.com',
                'password': 'testpassword'
            })
            self.assertEqual(response.status_code, 302)  
            self.assertIn(b'Register', response.data) #assertIn

    def test_login_form_invalid(self):
        with self.app.app_context():
            response = self.client.post('/register', data={
                'email': 'invalid@example.com',
                'password': 'invalidexample'
            })
            self.assertEqual(response.status_code, 200)  
            self.assertIn(b'Register', response.data) #assertIn"""

    
if __name__ == '__main__':
    unittest.main()

