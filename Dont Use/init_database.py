#!/usr/bin/env python3
"""
Database initialization script for CMS Pro
This script creates the database and tables if they don't exist
"""

import mysql.connector
from mysql.connector import Error
import sys

def create_database():
    """Create the database and tables"""
    
    # Database configuration
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Violin@12',
        'port': 3306
    }
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS food")
            print("✅ Database 'food' created or already exists")
            
            # Use the food database
            cursor.execute("USE food")
            
            # Create tables
            create_tables(cursor)
            
            # Insert sample data
            insert_sample_data(cursor)
            
            connection.commit()
            print("✅ Database initialization completed successfully!")
            
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure MySQL is running")
        print("2. Check if the password 'Violin@12' is correct")
        print("3. Try connecting with MySQL Workbench or phpMyAdmin")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ MySQL connection closed")
    
    return True

def create_tables(cursor):
    """Create all required tables"""
    
    # Locations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE
        )
    """)
    print("✅ Locations table created")
    
    # Departments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE
        )
    """)
    print("✅ Departments table created")
    
    # Roles Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE
        )
    """)
    print("✅ Roles table created")
    
    # Employees Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255),
            department_id INT,
            location_id INT,
            role_id INT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id),
            FOREIGN KEY (location_id) REFERENCES locations(id),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
    """)
    print("✅ Employees table created")
    
    # Vendors Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            contact_info VARCHAR(255)
        )
    """)
    print("✅ Vendors table created")
    
    # Meals Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name ENUM('Breakfast', 'Lunch', 'Dinner') NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            cost DECIMAL(10,2) NOT NULL,
            subsidy DECIMAL(10,2) NOT NULL
        )
    """)
    print("✅ Meals table created")
    
    # Bookings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT NOT NULL,
            meal_id INT NOT NULL,
            booking_date DATE NOT NULL,
            shift ENUM('Breakfast', 'Lunch', 'Dinner') NOT NULL,
            recurrence ENUM('None', 'Daily', 'Weekly') DEFAULT 'None',
            status ENUM('Booked', 'Consumed', 'Cancelled') DEFAULT 'Booked',
            location_id INT NOT NULL,
            qr_code_data TEXT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            consumed_at TIMESTAMP NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (meal_id) REFERENCES meals(id),
            FOREIGN KEY (location_id) REFERENCES locations(id)
        )
    """)
    print("✅ Bookings table created")
    
    # QR Tokens Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qr_tokens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT NOT NULL,
            token VARCHAR(255) NOT NULL UNIQUE,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            scanned_at TIMESTAMP NULL,
            status ENUM('Active', 'Scanned', 'Expired') DEFAULT 'Active',
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
    """)
    print("✅ QR Tokens table created")
    
    # Meal Consumption Log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meal_consumption_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT NOT NULL,
            employee_id INT NOT NULL,
            meal_id INT NOT NULL,
            location_id INT NOT NULL,
            consumed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            staff_id INT,
            FOREIGN KEY (booking_id) REFERENCES bookings(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (meal_id) REFERENCES meals(id),
            FOREIGN KEY (location_id) REFERENCES locations(id),
            FOREIGN KEY (staff_id) REFERENCES employees(id)
        )
    """)
    print("✅ Meal Consumption Log table created")

    # Special Messages Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS special_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message_text TEXT NOT NULL,
            is_active BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Special Messages table created")

def insert_sample_data(cursor):
    """Insert sample data into tables"""
    
    # Insert Locations
    locations = [('Unit 1',), ('Unit 2',), ('Unit 3',), ('Unit 4',), ('Unit 5',), ('Pallavaram',)]
    for location in locations:
        cursor.execute("INSERT IGNORE INTO locations (name) VALUES (%s)", location)
    print("✅ Sample locations inserted")
    
    # Insert Roles
    roles = [('Employee',), ('Staff',), ('Supervisor',), ('HR',), ('Accounts',), ('Admin',)]
    for role in roles:
        cursor.execute("INSERT IGNORE INTO roles (name) VALUES (%s)", role)
    print("✅ Sample roles inserted")
    
    # Insert Departments
    departments = [('IT',), ('HR',), ('Finance',), ('Operations',), ('Admin',)]
    for dept in departments:
        cursor.execute("INSERT IGNORE INTO departments (name) VALUES (%s)", dept)
    print("✅ Sample departments inserted")
    
    # Insert Meals
    meals = [
        ('Breakfast', '07:00:00', '09:00:00', 50.00, 30.00),
        ('Lunch', '12:00:00', '14:00:00', 100.00, 60.00),
        ('Dinner', '19:00:00', '21:00:00', 80.00, 50.00)
    ]
    for meal in meals:
        cursor.execute("INSERT IGNORE INTO meals (name, start_time, end_time, cost, subsidy) VALUES (%s, %s, %s, %s, %s)", meal)
    print("✅ Sample meals inserted")
    
    # Insert a sample employee for testing
    import hashlib
    password_hash = hashlib.sha256('password123'.encode()).hexdigest()
    
    cursor.execute("""
        INSERT IGNORE INTO employees (employee_id, name, email, password_hash, department_id, location_id, role_id)
        VALUES ('EMP001', 'John Doe', 'john.doe@violintec.com', %s, 1, 1, 2)
    """, (password_hash,))
    print("✅ Sample employee inserted")

if __name__ == "__main__":
    print("🚀 Initializing CMS Pro Database...")
    success = create_database()
    if success:
        print("\n🎉 Database setup completed! You can now run the Flask application.")
    else:
        print("\n❌ Database setup failed. Please check the error messages above.")
        sys.exit(1) 