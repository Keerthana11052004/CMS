#!/usr/bin/env python3
"""
Robust Database Schema Fix Script
Handles existing data properly when updating schema for QR code functionality
"""

import sys
from app import mysql
from app import create_app

app = create_app()

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT e.name, e.employee_id, l.name as location_name, b.booking_date, b.shift
        FROM bookings b
        JOIN employees e ON b.employee_id = e.id
        JOIN locations l ON b.location_id = l.id
        WHERE b.status = 'Booked'
    ''')
    rows = cur.fetchall()
    if not rows:
        print('No booked meals found.')
    else:
        print('Valid QR code strings for manual entry:')
        for row in rows:
            qr_string = f"{row['name']},{row['employee_id']},{row['location_name']},{row['booking_date']},{row['shift']}"
            print(qr_string) 