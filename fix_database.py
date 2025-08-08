import subprocess
import sys

def install_and_run():
    """Install mysql-connector-python and then create the table."""
    try:
        print("🐍 Ensuring mysql-connector-python is installed...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mysql-connector-python"])
        print("✅ mysql-connector-python is installed.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install mysql-connector-python: {e}")
        return

    import mysql.connector
    from mysql.connector import Error

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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS special_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message_text TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.commit()
            print("✅ 'special_messages' table created successfully.")
    except Error as e:
        print(f"❌ Error while connecting to MySQL or creating table: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ MySQL connection closed.")

if __name__ == '__main__':
    install_and_run()