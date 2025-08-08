#!/usr/bin/env python3
"""
Test MySQL connection with Flask-MySQLdb
"""

import sys
import traceback

def test_flask_mysql_connection():
    """Test MySQL connection using Flask-MySQLdb"""
    try:
        from flask import Flask
        from flask_mysqldb import MySQL
        
        # Create a minimal Flask app
        app = Flask(__name__)
        app.config['MYSQL_HOST'] = '127.0.0.1'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = 'Violin@12'
        app.config['MYSQL_DB'] = 'food'
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        app.config['MYSQL_PORT'] = 3306
        app.config['MYSQL_CHARSET'] = 'utf8mb4'
        app.config['MYSQL_AUTOCOMMIT'] = True
        app.config['MYSQL_CONNECT_TIMEOUT'] = 10
        
        mysql = MySQL()
        mysql.init_app(app)
        
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("SELECT 1")
            result = cur.fetchone()
            print("✅ Flask-MySQLdb connection successful!")
            print(f"Test query result: {result}")
            
            # Test if food database exists
            cur.execute("SHOW DATABASES")
            databases = cur.fetchall()
            db_names = [db['Database'] for db in databases]
            print(f"Available databases: {db_names}")
            
            if 'food' in db_names:
                print("✅ 'food' database found!")
                
                # Test if bookings table exists
                cur.execute("USE food")
                cur.execute("SHOW TABLES")
                tables = cur.fetchall()
                table_names = [table[f'Tables_in_food'] for table in tables]
                print(f"Tables in 'food' database: {table_names}")
                
                if 'bookings' in table_names:
                    print("✅ 'bookings' table found!")
                    
                    # Test bookings table structure
                    cur.execute("DESCRIBE bookings")
                    columns = cur.fetchall()
                    print("Bookings table columns:")
                    for col in columns:
                        print(f"  - {col['Field']}: {col['Type']}")
                    
                    # Test sample query
                    cur.execute("SELECT COUNT(*) as count FROM bookings")
                    count = cur.fetchone()
                    print(f"Total bookings: {count['count']}")
                    
                else:
                    print("❌ 'bookings' table not found!")
            else:
                print("❌ 'food' database not found!")
                
    except Exception as e:
        print(f"❌ Flask-MySQLdb connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        print("Full traceback:")
        traceback.print_exc()
        return False
    
    return True

def test_mysql_connector():
    """Test MySQL connection using mysql-connector-python"""
    try:
        import mysql.connector
        from mysql.connector import Error
        
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='Violin@12',
            database='food',
            port=3306,
            charset='utf8mb4'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ mysql-connector-python connection successful!")
            print(f"Test query result: {result}")
            
            # Test bookings table
            cursor.execute("SELECT COUNT(*) as count FROM bookings")
            count = cursor.fetchone()
            print(f"Total bookings: {count['count']}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ mysql-connector-python connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing MySQL connections...")
    print("\n1. Testing Flask-MySQLdb connection:")
    flask_success = test_flask_mysql_connection()
    
    print("\n2. Testing mysql-connector-python connection:")
    connector_success = test_mysql_connector()
    
    print(f"\n📊 Results:")
    print(f"Flask-MySQLdb: {'✅ Success' if flask_success else '❌ Failed'}")
    print(f"mysql-connector: {'✅ Success' if connector_success else '❌ Failed'}")
    
    if not flask_success and not connector_success:
        print("\n❌ Both connection methods failed. Please check:")
        print("1. MySQL service is running")
        print("2. Password 'Violin@12' is correct")
        print("3. Database 'food' exists")
        print("4. Port 3306 is accessible") 