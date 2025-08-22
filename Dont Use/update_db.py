import mysql.connector
from mysql.connector import Error

def update_vendor_table():
    """Update the vendors table with new columns"""
    
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
            
            # Add new columns to vendors table
            try:
                cursor.execute("ALTER TABLE vendors ADD COLUMN food_licence_status VARCHAR(255) DEFAULT 'Pending'")
                print("✅ Column 'food_licence_status' added.")
            except Error as e:
                if e.errno == 1060:  # Duplicate column name
                    print("⚠️ Column 'food_licence_status' already exists.")
                else:
                    raise e
            
            try:
                cursor.execute("ALTER TABLE vendors ADD COLUMN agreement_date DATE")
                print("✅ Column 'agreement_date' added.")
            except Error as e:
                if e.errno == 1060:  # Duplicate column name
                    print("⚠️ Column 'agreement_date' already exists.")
                else:
                    raise e
            print("✅ Vendors table updated successfully")
            
            connection.commit()
            
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ MySQL connection closed")

if __name__ == "__main__":
    print("🚀 Updating vendors table...")
    update_vendor_table()