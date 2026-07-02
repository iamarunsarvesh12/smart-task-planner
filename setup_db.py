import mysql.connector

try:
    db = mysql.connector.connect(host="localhost", user="root", password="BlckPrl#03")
    cursor = db.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS task_manager_db")
    cursor.execute("USE task_manager_db")
    
    # 1. Drop old tables to apply new Email rules
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("DROP TABLE IF EXISTS chat_history;")
    cursor.execute("DROP TABLE IF EXISTS tasks;")
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    # 2. UPGRADED: Email is now UNIQUE and NOT NULL
    cursor.execute("""
    CREATE TABLE users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        mobile VARCHAR(15)
    )""")

    cursor.execute("""
    CREATE TABLE tasks (
        task_id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        status ENUM('pending', 'in-progress', 'completed') DEFAULT 'pending',
        category ENUM('Personal', 'Family', 'Work', 'Health'),
        due_date DATETIME,
        reminder_sent BOOLEAN DEFAULT FALSE,
        user_id INT,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )""")

    cursor.execute("""
    CREATE TABLE chat_history (
        history_id INT AUTO_INCREMENT PRIMARY KEY,
        task_id INT,
        user_id INT,
        user_message TEXT,
        ai_response TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")
    
    db.commit()
    print("Database reset and optimized for Email Login!")

except mysql.connector.Error as err:
    print(f"Error: {err}")
