from flask import Flask, render_template, request, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
from flask_babel import Babel
import os

# Initialize extensions
mysql = MySQL()
login_manager = LoginManager()
bootstrap = Bootstrap()
csrf = CSRFProtect()
babel = Babel()

# User class
class User(UserMixin):
    def __init__(self, id, name='Guest', email=None, role=None, department=None, location=None, employee_id=None):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.department = department
        self.location = location
        self.employee_id = employee_id

# User loader
@login_manager.user_loader
def load_user(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE id=%s", (user_id,))
        user = cur.fetchone()
        if user:
            role_map = {1: 'Employee', 2: 'Staff', 3: 'Supervisor', 4: 'HR', 5: 'Accounts', 6: 'Admin'}
            role = role_map.get(user['role_id'], 'Employee')
            department = None
            if 'department_id' in user and user['department_id']:
                cur.execute("SELECT name FROM departments WHERE id=%s", (user['department_id'],))
                dept = cur.fetchone()
                if dept:
                    department = dept['name']
            location = None
            if 'location_id' in user and user['location_id']:
                cur.execute("SELECT name FROM locations WHERE id=%s", (user['location_id'],))
                loc = cur.fetchone()
                if loc:
                    location = loc['name']
            return User(user['id'], name=user['name'], email=user['email'], role=role, department=department, location=location, employee_id=user['employee_id'])
    except:
        pass
    return None

# App factory
def create_app():
    app = Flask(__name__, static_folder='static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-in-production')
    app.config['LANGUAGES'] = ['en', 'ta', 'hi']
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'

    # MySQL config
    app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', '127.0.0.1')
    app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'Violin@12')
    app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'food')
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    mysql.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)

    def get_locale():
        if request.args.get('lang'):
            session['lang'] = request.args.get('lang')
        return session.get('lang', app.config['BABEL_DEFAULT_LOCALE'])

    babel.init_app(app, locale_selector=get_locale)

    # Register blueprints
    from .cms import cms_blueprint
    from .employee import employee_bp
    from .staff import staff_bp
    from .admin import admin_bp

    app.register_blueprint(cms_blueprint, url_prefix='/cms')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    @app.route('/')
    def index():
        current_lang = session.get('lang', app.config['BABEL_DEFAULT_LOCALE'])
        return render_template('index.html', current_lang=current_lang)

    return app
