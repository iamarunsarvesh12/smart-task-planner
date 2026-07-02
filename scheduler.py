import time
from plyer import notification
import db_manager

# UPGRADED: Now accepts user_id
def check_for_reminders(user_id):
    conn = db_manager.create_connection()
    if not conn: return

    try:
        cursor = conn.cursor(dictionary=True)
        # Added 'AND user_id = %s' to only get this specific user's tasks
        sql = """
            SELECT task_id, title, due_date 
            FROM tasks 
            WHERE status != 'completed' 
            AND reminder_sent = FALSE 
            AND due_date > NOW() 
            AND due_date <= DATE_ADD(NOW(), INTERVAL 10 MINUTE)
            AND user_id = %s
        """
        cursor.execute(sql, (user_id,))
        tasks_due = cursor.fetchall()

        for task in tasks_due:
            formatted_time = task['due_date'].strftime('%I:%M %p')
            
            notification.notify(
                title="AI Task Manager Alert!",
                message=f"Your task '{task['title']}' is coming up at {formatted_time}.",
                app_name="AI Task Manager",
                timeout=10 
            )
            
            update_sql = "UPDATE tasks SET reminder_sent = TRUE WHERE task_id = %s"
            cursor.execute(update_sql, (task['task_id'],))
            conn.commit()

    except Exception as e:
        print(f"Scheduler Error: {e}")
    finally:
        cursor.close()
        conn.close()
