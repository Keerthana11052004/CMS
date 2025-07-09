from flask import Flask, render_template
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect

mysql = MySQL()
login_manager = LoginManager()
bootstrap = Bootstrap()
csrf = CSRFProtect()

class User(UserMixin):
    def __init__(self, id, name='Guest', email=None, role=None):
        self.id = id
        self.name = name
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employees WHERE id=%s", (user_id,))
    user = cur.fetchone()
    if user:
        role_map = {1: 'Employee', 2: 'Staff', 3: 'Supervisor', 4: 'HR', 5: 'Accounts', 6: 'Admin'}
        role = role_map.get(user['role_id'], 'Employee')
        return User(user['id'], name=user['name'], email=user['email'], role=role)
    return None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'Violin@12'
    app.config['MYSQL_DB'] = 'food'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    mysql.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)

    from .employee import employee_bp
    from .staff import staff_bp
    from .admin import admin_bp
    app.register_blueprint(employee_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app 