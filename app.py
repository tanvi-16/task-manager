from flask import Flask, render_template, request, redirect
from flask import Flask, render_template, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import pytz  

db = SQLAlchemy()
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class RegisterForm(FlaskForm):
    username =  StringField('username', validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Sign Up')
    csrf_token = HiddenField('CSRF Token')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')
    csrf_token = HiddenField('CSRF Token')


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ENFEFKNDEWJFNESFSDFF'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Lenovo@localhost/flask_auth_db'
    bcrypt =  Bcrypt()
    db.init_app(app) 
    bcrypt.init_app(app)   
    with app.app_context():
        db.create_all()

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function


    @app.route('/', methods=["GET", "POST"])
    @login_required
    def index():
        if request.method == "POST":
            user_title = request.form["title"]
            user_desc = request.form["desc"]

            ist_tz = pytz.timezone('Asia/Kolkata')
            ist_datetime = datetime.now(tz=ist_tz)
            date_format = '%d-%m-%Y %H:%M:%S'
            date_str = ist_datetime.strftime(date_format)
            date_created = datetime.strptime(date_str, date_format)

            todo = Todo(title=user_title, desc=user_desc,
                        date_created=date_created)
            db.session.add(todo)
            db.session.commit()

        all_items = Todo.query.all()
        return render_template("index.html", all_todos=all_items)
    
    @app.route("/update/<int:sno>", methods=["GET", "POST"])
    @login_required
    def update_item(sno):
        if request.method == "POST":
            user_title = request.form["title"]
            user_desc = request.form["desc"]

            item = Todo.query.get_or_404(sno)
            item.title = user_title
            item.desc = user_desc
            db.session.add(item)
            db.session.commit()
            return redirect("/")

        item = Todo.query.get_or_404(sno)
        return render_template("update.html", todo=item)
    
    @app.route('/delete/<int:sno>')
    @login_required
    def delete_item(sno):
        item = Todo.query.get_or_404(sno)
        db.session.delete(item)
        db.session.commit()
        return redirect('/')
    

    @app.route('/search', methods=["GET", "POST"])
    @login_required
    def search_item():
        search_query = request.args.get('query')
        result = Todo.query.filter(Todo.title == search_query).all()
        return render_template('result.html', posts=result)
    
    @app.route('/login', methods=['GET','POST'])
    def login():
        if 'user_id' in session:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                session['user_id']= user.id
                session['username']=user.username
                flash('You have been logged in !', 'Success')
                return redirect(url_for('index'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'Danger')
        return render_template('login.html', form=form)
    
    @app.route('/register' , methods=['GET','POST'])
    def register():
        if 'user_id' in session:
            return redirect(url_for('index'))
        form =  RegisterForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
            )
            db.session.add(user)
            db.session.commit()
            flash('Account has been created!!!','success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        session.pop('user_id')
        session.pop('username')
        flash('You have been logged out !!','Success')
        return redirect(url_for('index'))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)