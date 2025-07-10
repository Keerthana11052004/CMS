from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, make_response
from flask_login import login_required, login_user, logout_user, current_user
from app import mysql, User
import hashlib
from app.forms import LoginForm, AddUserForm
import csv
import io
import pandas as pd

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE email=%s AND role_id=6 AND is_active=1", (email,))
        user = cur.fetchone()
        if user:
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] == password_hash or user['password_hash'] == password:
                user_obj = User(user['id'], name=user['name'], email=user['email'], role='Admin')
                login_user(user_obj)
                flash('Login successful!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid password.', 'danger')
        else:
            flash('Invalid email or not an admin.', 'danger')
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    # Total bookings
    cur.execute('SELECT COUNT(*) AS total FROM bookings')
    total_bookings = cur.fetchone()['total']
    # Consumed meals
    cur.execute("SELECT COUNT(*) AS consumed FROM bookings WHERE status='Consumed'")
    consumed_meals = cur.fetchone()['consumed']
    # Booked meals (not yet consumed)
    cur.execute("SELECT COUNT(*) AS booked FROM bookings WHERE status='Booked'")
    booked_meals = cur.fetchone()['booked']
    # Trends (last 7 days bookings)
    cur.execute("SELECT booking_date, COUNT(*) as count FROM bookings WHERE booking_date >= CURDATE() - INTERVAL 6 DAY GROUP BY booking_date ORDER BY booking_date")
    trends = cur.fetchall()
    return render_template('admin/dashboard.html',
        total_bookings=total_bookings,
        consumed_meals=consumed_meals,
        booked_meals=booked_meals,
        trends=trends
    )

@admin_bp.route('/employee_reports')
@login_required
def employee_reports():
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT e.name as employee, d.name as department, e.id as employee_id
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
    ''')
    employees = cur.fetchall()
    return render_template('admin/employee_reports.html', employees=employees)

@admin_bp.route('/dept_location_reports')
@login_required
def dept_location_reports():
    # TODO: Department/location reports
    return render_template('admin/dept_location_reports.html')

@admin_bp.route('/cost_subsidy')
@login_required
def cost_subsidy():
    # TODO: Cost & subsidy analysis
    return render_template('admin/cost_subsidy.html')

@admin_bp.route('/vendor_report')
@login_required
def vendor_report():
    # TODO: Monthly vendor report
    return render_template('admin/vendor_report.html')

@admin_bp.route('/export')
@login_required
def export():
    # TODO: Export data as Excel/CSV
    return render_template('admin/export.html')

@admin_bp.route('/export_employee_report')
@login_required
def export_employee_report():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('admin.dashboard'))
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT e.name as employee, d.name as department, 
               COUNT(b.id) as meals_booked,
               SUM(CASE WHEN b.status = 'Consumed' THEN 1 ELSE 0 END) as meals_consumed
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN bookings b ON e.id = b.employee_id
        GROUP BY e.id, d.name
    ''')
    rows = cur.fetchall()
    # Create CSV in memory
    output = []
    header = ['Employee', 'Department', 'Meals Booked', 'Meals Consumed']
    output.append(header)
    for row in rows:
        output.append([
            row['employee'],
            row['department'],
            row['meals_booked'],
            row['meals_consumed']
        ])
    # Convert to CSV string
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerows(output)
    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=employee_report.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@admin_bp.route('/export_meal_excel')
@login_required
def export_meal_excel():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('admin.export'))
    # Get filters from request.args
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    department = request.args.get('department')
    location = request.args.get('location')
    cur = mysql.connection.cursor()
    query = '''
        SELECT e.name as employee, d.name as department, l.name as location, b.booking_date, b.shift, b.status
        FROM bookings b
        JOIN employees e ON b.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN locations l ON b.location_id = l.id
        WHERE 1=1
    '''
    params = []
    if start_date:
        query += ' AND b.booking_date >= %s'
        params.append(start_date)
    if end_date:
        query += ' AND b.booking_date <= %s'
        params.append(end_date)
    if department:
        query += ' AND d.name = %s'
        params.append(department)
    if location:
        query += ' AND l.name = %s'
        params.append(location)
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    df = pd.DataFrame(rows)
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Meal Data')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='meal_data.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@admin_bp.route('/export_meal_csv')
@login_required
def export_meal_csv():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('admin.export'))
    # Get filters from request.args
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    department = request.args.get('department')
    location = request.args.get('location')
    cur = mysql.connection.cursor()
    query = '''
        SELECT e.name as employee, d.name as department, l.name as location, b.booking_date, b.shift, b.status
        FROM bookings b
        JOIN employees e ON b.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN locations l ON b.location_id = l.id
        WHERE 1=1
    '''
    params = []
    if start_date:
        query += ' AND b.booking_date >= %s'
        params.append(start_date)
    if end_date:
        query += ' AND b.booking_date <= %s'
        params.append(end_date)
    if department:
        query += ' AND d.name = %s'
        params.append(department)
    if location:
        query += ' AND l.name = %s'
        params.append(location)
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    import csv
    import io
    si = io.StringIO()
    if rows:
        writer = csv.DictWriter(si, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=meal_data.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('admin.dashboard'))
    form = AddUserForm()
    cur = mysql.connection.cursor()
    # Populate select field choices
    cur.execute('SELECT id, name FROM departments')
    departments = cur.fetchall()
    form.department_id.choices = [(d['id'], d['name']) for d in departments]
    cur.execute('SELECT id, name FROM locations')
    locations = cur.fetchall()
    form.location_id.choices = [(l['id'], l['name']) for l in locations]
    cur.execute('SELECT id, name FROM roles')
    roles = cur.fetchall()
    form.role_id.choices = [(r['id'], r['name']) for r in roles]
    if form.validate_on_submit():
        employee_id = form.employee_id.data
        name = form.name.data
        email = form.email.data
        password = form.password.data
        department_id = form.department_id.data
        location_id = form.location_id.data
        role_id = form.role_id.data
        is_active = 1 if form.is_active.data else 0
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            cur.execute("INSERT INTO employees (employee_id, name, email, password_hash, department_id, location_id, role_id, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (employee_id, name, email, password_hash, department_id, location_id, role_id, is_active))
            mysql.connection.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('admin.add_user'))
        except Exception as e:
            flash('Error adding user: ' + str(e), 'danger')
    # Debug: print CSRF token value
    print('CSRF token in form:', getattr(form, 'csrf_token', None))
    return render_template('admin/add_user.html', form=form)

@admin_bp.route('/debug_routes')
def debug_routes():
    from flask import current_app
    output = []
    for rule in current_app.url_map.iter_rules():
        output.append(f"{rule.endpoint}: {rule}")
    return '<br>'.join(output) 