from flask import Blueprint, render_template, redirect, url_for, request, flash, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm, BookMealForm
from app.utils import generate_meal_qr_code
from app import mysql, User
import hashlib

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

@employee_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE email=%s AND role_id=1 AND is_active=1", (email,))
        user = cur.fetchone()
        if user:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] == password_hash or user['password_hash'] == password:
                user_obj = User(user['id'], name=user['name'], email=user['email'], role='Employee')
                login_user(user_obj)
                flash('Login successful!', 'success')
                return redirect(url_for('employee.dashboard'))
            else:
                flash('Invalid password.', 'danger')
        else:
            flash('Invalid email or not an employee.', 'danger')
    return render_template('employee/login.html', form=form)

@employee_bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@employee_bp.route('/dashboard')
@login_required
def dashboard():
    # TODO: Show welcome, quick links, today status
    return render_template('employee/dashboard.html')

@employee_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book_meal():
    form = BookMealForm()
    qr_image_base64 = None
    if form.validate_on_submit():
        shift = form.shift.data
        date = form.date.data
        recurrence = form.recurrence.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM meals WHERE name=%s", (shift,))
        meal = cur.fetchone()
        if not meal:
            flash('Invalid meal/shift selected.', 'danger')
            return redirect(url_for('employee.book_meal'))
        meal_id = meal['id']
        employee_id = current_user.id
        cur.execute("SELECT location_id FROM employees WHERE id=%s", (employee_id,))
        emp = cur.fetchone()
        if not emp or not emp['location_id']:
            flash('Your location is not set. Contact admin.', 'danger')
            return redirect(url_for('employee.book_meal'))
        location_id = emp['location_id']
        cur.execute("SELECT e.name, e.employee_id, l.name as location_name FROM employees e JOIN locations l ON e.location_id = l.id WHERE e.id=%s", (employee_id,))
        emp_details = cur.fetchone()
        if not emp_details:
            flash('Employee details not found.', 'danger')
            return redirect(url_for('employee.book_meal'))
        qr_image_base64, qr_data_json = generate_meal_qr_code(
            employee_name=emp_details['name'],
            employee_id=emp_details['employee_id'],
            unit_name=emp_details['location_name'],
            date=str(date),
            shift=shift
        )
        try:
            cur.execute("INSERT INTO bookings (employee_id, meal_id, booking_date, shift, recurrence, location_id, status, qr_code_data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (employee_id, meal_id, date, shift, recurrence, location_id, 'Booked', qr_image_base64))
            mysql.connection.commit()
            flash('Meal booked successfully! QR code generated.', 'success')
            # Instead of redirect, render the form with QR code
            return render_template('employee/book.html', form=form, qr_image_base64=qr_image_base64)
        except Exception as e:
            flash('Error booking meal: ' + str(e), 'danger')
            return redirect(url_for('employee.book_meal'))
    return render_template('employee/book.html', form=form, qr_image_base64=qr_image_base64)

@employee_bp.route('/history')
@login_required
def booking_history():
    cur = mysql.connection.cursor()
    
    # Get user's bookings with QR codes
    cur.execute("""
        SELECT b.*, m.name as meal_name, l.name as location_name, e.name as employee_name, e.employee_id
        FROM bookings b
        JOIN meals m ON b.meal_id = m.id
        JOIN locations l ON b.location_id = l.id
        JOIN employees e ON b.employee_id = e.id
        WHERE b.employee_id = %s
        ORDER BY b.booking_date DESC, b.created_at DESC
    """, (current_user.id,))
    
    bookings = cur.fetchall()
    return render_template('employee/history.html', bookings=bookings)

@employee_bp.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    cur = mysql.connection.cursor()
    # Check if booking exists and belongs to current user and is 'Booked'
    cur.execute("SELECT * FROM bookings WHERE id=%s AND employee_id=%s", (booking_id, current_user.id))
    booking = cur.fetchone()
    if not booking:
        flash('Booking not found or not authorized.', 'danger')
        return redirect(url_for('employee.booking_history'))
    if booking['status'] != 'Booked':
        flash('Only booked meals can be cancelled.', 'warning')
        return redirect(url_for('employee.booking_history'))
    # Update status to Cancelled
    cur.execute("UPDATE bookings SET status='Cancelled' WHERE id=%s", (booking_id,))
    mysql.connection.commit()
    flash('Booking cancelled successfully.', 'success')
    return redirect(url_for('employee.booking_history'))

@employee_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        department_id = request.form.get('department_id') or None
        location_id = request.form.get('location_id') or None
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Password update logic
        if password:
            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
            else:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cur.execute("UPDATE employees SET password_hash=%s WHERE id=%s", (password_hash, current_user.id))
                mysql.connection.commit()
                flash('Password updated successfully.', 'success')

        # Update name, department, location
        cur.execute(
            "UPDATE employees SET name=%s, department_id=%s, location_id=%s WHERE id=%s",
            (name, department_id, location_id, current_user.id)
        )
        mysql.connection.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('employee.profile'))

    # Get current employee details
    cur.execute("""
        SELECT e.*, d.name as department_name, l.name as location_name 
        FROM employees e 
        LEFT JOIN departments d ON e.department_id = d.id 
        LEFT JOIN locations l ON e.location_id = l.id 
        WHERE e.id = %s
    """, (current_user.id,))
    employee = cur.fetchone()

    # Get all locations and departments for dropdowns
    cur.execute("SELECT id, name FROM locations ORDER BY name")
    locations = cur.fetchall()
    cur.execute("SELECT id, name FROM departments ORDER BY name")
    departments = cur.fetchall()

    return render_template('employee/profile.html', employee=employee, locations=locations, departments=departments) 