import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
import random

# --- EMAIL CONFIGURATION ---
# To send real emails, replace these with your Gmail and a 16-digit Google App Password
SENDER_EMAIL = "your_email@gmail.com" 
SENDER_PASSWORD = "your_app_password"

def create_connection():
    try:
        return mysql.connector.connect(host='localhost', database='task_manager_db', user='root', password='BlckPrl#03')
    except Error as e:
        print(f"Error connecting: {e}")
        return None

# ==========================================
# Authentication & OTP Functions
# ==========================================
def register_user(username, password, email, mobile):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO users (username, password, email, mobile) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, password, email, mobile))
            conn.commit()
            return True, "Registration successful!"
        except Error as e:
            if "Duplicate entry" in str(e):
                return False, "This Email is already registered!"
            return False, f"Database error: {e}"
        finally:
            cursor.close()
            conn.close()

def verify_login(email, password):
    """UPGRADED: Now checks EMAIL instead of Username"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT user_id FROM users WHERE email = %s AND password = %s"
            cursor.execute(sql, (email, password))
            user = cursor.fetchone()
            if user: return True, user['user_id']
            else: return False, "Invalid Email or Password."
        except Error as e: return False, str(e)
        finally:
            cursor.close()
            conn.close()
    return False, None

def send_otp_email(recipient_email):
    """Generates a 6-digit OTP and attempts to email it."""
    otp = str(random.randint(100000, 999999))
    
    # DEVELOPER FALLBACK: Prints the OTP to your terminal so you can test it 
    # even if your Gmail credentials aren't set up yet!
    print(f"\n[{recipient_email}] -> TEST MODE OTP: {otp}\n") 
    
    try:
        msg = MIMEText(f"Your AI Task Manager password reset OTP is: {otp}\nDo not share this with anyone.")
        msg['Subject'] = 'Password Reset OTP'
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True, otp
    except Exception as e:
        print("Real email failed to send (using Terminal Fallback).")
        return True, otp # We return True so the GUI continues to the next screen anyway

def update_password(email, new_password):
    """Saves the newly reset password to the database."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql = "UPDATE users SET password = %s WHERE email = %s"
            cursor.execute(sql, (new_password, email))
            conn.commit()
        except Error as e: print(f"Failed to update password: {e}")
        finally:
            cursor.close()
            conn.close()

# ==========================================
# Task Management Functions (Unchanged)
# ==========================================
def add_task(title, description, category, due_datetime, user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO tasks (title, description, category, due_date, user_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (title, description, category, due_datetime, user_id))
            conn.commit()
        except Error as e: print(e)
        finally: cursor.close(); conn.close()

def get_pending_tasks(user_id):
    conn = create_connection()
    tasks = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True) 
            sql = "SELECT * FROM tasks WHERE status != 'completed' AND user_id = %s"
            cursor.execute(sql, (user_id,))
            tasks = cursor.fetchall()
        except Error as e: print(e)
        finally: cursor.close(); conn.close()
    return tasks

def delete_task(task_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
            conn.commit()
        except Error as e: print(e)
        finally: cursor.close(); conn.close()

def update_task_title(task_id, new_title):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET title = %s WHERE task_id = %s", (new_title, task_id))
            conn.commit()
        except Error as e: print(e)
        finally: cursor.close(); conn.close()
