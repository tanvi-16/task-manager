import unittest
from app import create_app, db
from app import User, Todo
from flask_bcrypt import Bcrypt
from datetime import datetime

class TestModels(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Lenovo@localhost/flask_auth_db'
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'ENFEFKNDEWJFNESFSDFF'
        bcrypt = Bcrypt()
        bcrypt.init_app(self.app)
        app_context = self.app.app_context()
        app_context.push()

        with self.app.app_context():
            db.create_all()
        hashed_password = bcrypt.generate_password_hash('testpassword').decode('utf-8')
        user = User(username='testuser', email='test@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()
        self.app_context = app_context

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_model(self):
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.password.startswith('$2b$'))

    def test_todo_model(self):
        todo = Todo(title='Test Todo', desc='Test Description', date_created=datetime.utcnow())
        db.session.add(todo)
        db.session.commit()

        added_todo = Todo.query.first()
        self.assertEqual(added_todo.title, 'Test Todo')
        self.assertEqual(added_todo.desc, 'Test Description')


if __name__ == '__main__':
    unittest.main()

