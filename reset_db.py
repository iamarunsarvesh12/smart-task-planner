import mysql.connector

# Connect to the database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="BlckPrl#03",
    database="task_manager_db"
)
cursor = db.cursor()

# 1. Disable foreign key checks so we can wipe connected tables
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

# 2. Truncate (empty and reset ID to 1) all tables
cursor.execute("TRUNCATE TABLE chat_history;")
cursor.execute("TRUNCATE TABLE tasks;")
cursor.execute("TRUNCATE TABLE users;")

# 3. Turn checks back on
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
db.commit()

print("Database completely reset! All IDs will now start at 1.")

cursor.close()
db.close()
