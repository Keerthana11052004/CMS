import mysql.connector
from mysql.connector import Error

def update_vendor_table_for_uploads():
    """Updates the vendors table to support file uploads."""
    
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
            
            try:
                # Rename food_licence_status to food_licence_path
                cursor.execute("ALTER TABLE vendors CHANGE COLUMN food_licence_status food_licence_path VARCHAR(255)")
                print("✅ Column 'food_licence_status' renamed to 'food_licence_path'.")
            except Error as e:
                if e.errno == 1060:  # Duplicate column name
                    print("⚠️ Column 'food_licence_path' already exists.")
                elif 'Unknown column' in e.msg and 'food_licence_status' in e.msg:
                    print("⚠️ Column 'food_licence_status' does not exist, assuming 'food_licence_path' is already there.")
                else:
                    # If the column doesn't exist, maybe it was already renamed. Let's try adding it if it's not there.
                    try:
                        cursor.execute("ALTER TABLE vendors ADD COLUMN food_licence_path VARCHAR(255)")
                        print("✅ Column 'food_licence_path' added.")
                    except Error as add_e:
                         if add_e.errno == 1060:
                             print("⚠️ Column 'food_licence_path' already exists.")
                         else:
                             raise add_e
            
            connection.commit()
            
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ MySQL connection closed")

if __name__ == "__main__":
    print("🚀 Updating vendors table for file uploads...")
    update_vendor_table_for_uploads()