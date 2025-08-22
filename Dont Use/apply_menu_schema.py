import mysql.connector
from mysql.connector import Error
import os

def apply_schema_update():
    """Applies the SQL script to update the database schema."""
    
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Violin@12',
        'database': 'food',
        'port': 3306
    }
    
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Get the path to the SQL file
            sql_file_path = os.path.join(os.path.dirname(__file__), 'update_schema_for_menu.sql')

            with open(sql_file_path, 'r') as f:
                sql_script = f.read()
            
            # Split the script into individual statements
            sql_commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]

            # Execute each command
            for command in sql_commands:
                try:
                    cursor.execute(command)
                    print(f"✅ Executed: {command}")
                except Error as e:
                    # Ignore "table already exists" error
                    if e.errno == 1050:
                        print(f"⚠️  Table already exists, skipping: {command}")
                    else:
                        raise e

            print("✅ Database schema updated successfully from update_schema_for_menu.sql")
            connection.commit()
            
    except Error as e:
        print(f"❌ Error connecting to MySQL or executing script: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ MySQL connection closed")

if __name__ == "__main__":
    print("🚀 Applying schema update for daily menus...")
    apply_schema_update()