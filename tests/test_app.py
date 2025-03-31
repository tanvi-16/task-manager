import unittest
from app import create_app, db
from flask import session
from flask_testing import TestCase
from app import User, Todo
from flask_bcrypt import Bcrypt
from flask import url_for

class TestApp(TestCase):

    def create_app(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Lenovo@localhost/flask_auth_db'
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'ENFEFKNDEWJFNESFSDFF'
        bcrypt = Bcrypt()
        bcrypt.init_app(app)
        with app.app_context():
            db.create_all()
        return app

    def setUp(self):
        app = create_app()
        bcrypt = Bcrypt()
        bcrypt.init_app(app)
        with app.app_context():
            db.create_all()
        hashed_password = bcrypt.generate_password_hash('testpassword').decode('utf-8')
        user = User(username='testuser', email='test@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()  

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_register_page(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

    def test_index_page_redirect_if_not_logged_in(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302) 
        self.assertIn(b'login', response.data) 

    def test_login_functionality(self):
        response = self.client.post('/login', data=dict(email='test@example.com', password='testpassword'), follow_redirects=True)
        self.assertIn(b'Login', response.data)
        self.assertEqual(response.status_code, 200)

    def test_register_functionality(self):
        response = self.client.post('/register', data=dict(username='newuser', email='newuser@example.com', password='newpassword', confirm_password='newpassword'), follow_redirects=True)
        self.assertIn(b'Register', response.data)

    def test_add_todo(self):
        response = self.client.post('/', data=dict(title='Test Todo', desc='This is a test todo'), follow_redirects=True)
        self.assertIn(b'Login', response.data)

    def test_update_todo(self):
        todo = Todo(title='Old Title', desc='Old Description')
        db.session.add(todo)
        db.session.commit()
        response = self.client.post(f'/update/{todo.sno}', data=dict(title='Updated Title', desc='Updated Description'), follow_redirects=True)
        self.assertIn(b'Login', response.data)

    def test_delete_todo(self):
        todo = Todo(title='To Delete', desc='This todo will be deleted')
        db.session.add(todo)
        db.session.commit()
        response = self.client.get(f'/delete/{todo.sno}', follow_redirects=True)
        self.assertNotIn(b'To Delete', response.data)


if __name__ == '__main__':
    unittest.main()
