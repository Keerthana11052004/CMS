#!/usr/bin/env python3
"""
Final Database Schema Fix Script
Checks existing data and fixes schema properly for QR code functionality
"""

import mysql.connector
from mysql.connector import Error

def fix_database():
    """Fix the database schema for QR code functionality"""
    
    # Database configuration
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Violin@12',
        'database': 'food'
    }
    
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("🔧 Checking database schema...")
        
        # Check if qr_code_data column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'food' 
            AND TABLE_NAME = 'bookings' 
            AND COLUMN_NAME = 'qr_code_data'
        """)
        
        column_exists = cursor.fetchone()[0] > 0
        
        if not column_exists:
            print("➕ Adding qr_code_data column...")
            cursor.execute("""
                ALTER TABLE bookings 
                ADD COLUMN qr_code_data TEXT NULL AFTER location_id
            """)
            print("✅ qr_code_data column added successfully!")
        else:
            print("✅ qr_code_data column already exists")
        
        # Check what status values currently exist
        print("🔍 Checking current status values...")
        cursor.execute("SELECT DISTINCT status FROM bookings")
        existing_statuses = [row[0] for row in cursor.fetchall()]
        print(f"Found status values: {existing_statuses}")
        
        # Update any problematic status values
        if existing_statuses:
            print("🔄 Updating status values...")
            for status in existing_statuses:
                if status not in ['Booked', 'Consumed', 'Cancelled']:
                    print(f"Converting '{status}' to 'Booked'...")
                    cursor.execute("UPDATE bookings SET status = 'Booked' WHERE status = %s", (status,))
                    updated_count = cursor.fetchone()[0] if cursor.fetchone() else 0
                    print(f"Updated {updated_count} records")
        
        # Now safely update the status enum
        print("🔄 Updating status enum...")
        try:
            cursor.execute("""
                ALTER TABLE bookings 
                MODIFY COLUMN status ENUM('Booked', 'Consumed', 'Cancelled') DEFAULT 'Booked'
            """)
            print("✅ Status enum updated successfully!")
        except Error as e:
            print(f"⚠️ Warning: Could not update enum: {e}")
            print("Continuing with other updates...")
        
        # Add indexes if they don't exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_SCHEMA = 'food' 
            AND TABLE_NAME = 'bookings' 
            AND INDEX_NAME = 'idx_employee_date_shift'
        """)
        
        index1_exists = cursor.fetchone()[0] > 0
        
        if not index1_exists:
            print("➕ Adding performance indexes...")
            try:
                cursor.execute("""
                    CREATE INDEX idx_employee_date_shift 
                    ON bookings(employee_id, booking_date, shift)
                """)
                print("✅ Index 1 added successfully!")
            except Error as e:
                print(f"⚠️ Warning: Could not create index 1: {e}")
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_SCHEMA = 'food' 
            AND TABLE_NAME = 'bookings' 
            AND INDEX_NAME = 'idx_status'
        """)
        
        index2_exists = cursor.fetchone()[0] > 0
        
        if not index2_exists:
            try:
                cursor.execute("CREATE INDEX idx_status ON bookings(status)")
                print("✅ Index 2 added successfully!")
            except Error as e:
                print(f"⚠️ Warning: Could not create index 2: {e}")
        
        # Verify the changes
        cursor.execute("DESCRIBE bookings")
        columns = cursor.fetchall()
        print("\n📋 Current table structure:")
        for column in columns:
            print(f"  - {column[0]}: {column[1]}")
        
        # Check final status values
        cursor.execute("SELECT DISTINCT status FROM bookings")
        final_statuses = [row[0] for row in cursor.fetchall()]
        print(f"\n📊 Final status values: {final_statuses}")
        
        # Commit changes
        connection.commit()
        print("\n🎉 Database schema fixed successfully!")
        print("✅ QR code functionality is now ready to use!")
        
    except Error as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your MySQL password in the config")
        print("2. Ensure MySQL server is running")
        print("3. Verify the 'food' database exists")
        print("4. Check your MySQL user permissions")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Database connection closed")

if __name__ == "__main__":
    print("🚀 Starting final database schema fix...")
    fix_database() 