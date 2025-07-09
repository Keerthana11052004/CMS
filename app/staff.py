from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, login_user, logout_user
from app.forms import LoginForm
from app.utils import decode_qr_code

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        from app import mysql, User
        import hashlib
        email = form.email.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE email=%s AND role_id IN (2,3) AND is_active=1", (email,))
        user = cur.fetchone()
        if user:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] == password_hash or user['password_hash'] == password:
                role = 'Supervisor' if user['role_id'] == 3 else 'Staff'
                user_obj = User(user['id'], name=user['name'], email=user['email'], role=role)
                login_user(user_obj)
                flash('Login successful!', 'success')
                return redirect(url_for('staff.dashboard'))
            else:
                flash('Invalid password.', 'danger')
        else:
            flash('Invalid email or not staff.', 'danger')
    return render_template('staff/login.html', form=form)

@staff_bp.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@staff_bp.route('/qr_scanner')
@login_required
def qr_scanner():
    return render_template('staff/qr_scanner.html')

@staff_bp.route('/scan_qr', methods=['POST'])
@login_required
def scan_qr():
    from app import mysql
    qr_data = request.json.get('qr_data')
    
    if not qr_data:
        return jsonify({'success': False, 'message': 'No QR data provided'})
    
    # Decode QR data
    decoded_data = decode_qr_code(qr_data)
    if not decoded_data:
        return jsonify({'success': False, 'message': 'Invalid QR code format'})
    
    # Find the booking
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT b.*, e.name as employee_name, e.employee_id, l.name as location_name, m.name as meal_name
        FROM bookings b
        JOIN employees e ON b.employee_id = e.id
        JOIN locations l ON b.location_id = l.id
        JOIN meals m ON b.meal_id = m.id
        WHERE e.employee_id = %s AND b.booking_date = %s AND b.shift = %s AND b.status = 'Booked'
    """, (decoded_data['employee_id'], decoded_data['date'], decoded_data['shift']))
    
    booking = cur.fetchone()
    
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found or already consumed'})
    
    # Update booking status to consumed
    try:
        cur.execute("""
            UPDATE bookings 
            SET status = 'Consumed', consumed_at = NOW() 
            WHERE id = %s
        """, (booking['id'],))
        
        # Log the consumption
        cur.execute("""
            INSERT INTO meal_consumption_log (booking_id, employee_id, meal_id, location_id, staff_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (booking['id'], booking['employee_id'], booking['meal_id'], booking['location_id'], current_user.id))
        
        mysql.connection.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Meal consumed successfully for {booking["employee_name"]}',
            'booking': {
                'employee_name': booking['employee_name'],
                'employee_id': booking['employee_id'],
                'unit': booking['location_name'],
                'date': booking['booking_date'].strftime('%Y-%m-%d'),
                'shift': booking['shift']
            }
        })
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': f'Error processing meal: {str(e)}'})

@staff_bp.route('/dashboard')
@login_required
def dashboard():
    # TODO: Real-time meal count dashboard
    return render_template('staff/dashboard.html')

@staff_bp.route('/summary')
@login_required
def summary():
    # TODO: Daily summary report
    return render_template('staff/summary.html')

@staff_bp.route('/roles', methods=['GET', 'POST'])
@login_required
def manage_roles():
    # TODO: Role management for supervisors
    return render_template('staff/roles.html') 