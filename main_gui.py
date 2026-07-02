import customtkinter as ctk
from tkcalendar import Calendar
import threading
import time
import db_manager
import ai_brain
import scheduler

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AITaskManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Personal Assistant")
        self.geometry("1000x650")
        
        self.current_user_id = None 
        self.start_scheduler()
        
        # --- NEW: Master Theme Toggle Button ---
        self.current_theme = "Dark"
        self.theme_btn = ctk.CTkButton(self, text="☀️ Light Mode", width=100, command=self.toggle_theme, fg_color="transparent", border_width=1)
        self.theme_btn.place(relx=0.98, rely=0.02, anchor="ne") # Placed in top right corner
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=40) # Added padding so it doesn't overlap the theme button
        
        self.show_login_screen()

    def toggle_theme(self):
        if self.current_theme == "Dark":
            ctk.set_appearance_mode("Light")
            self.current_theme = "Light"
            self.theme_btn.configure(text="🌙 Dark Mode")
        else:
            ctk.set_appearance_mode("Dark")
            self.current_theme = "Dark"
            self.theme_btn.configure(text="☀️ Light Mode")

    def clear_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ==========================================
    # AUTHENTICATION SCREENS
    # ==========================================
    def show_login_screen(self):
        self.clear_screen()
        login_frame = ctk.CTkFrame(self.container)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(login_frame, text="Login to AI Assistant", font=("Arial", 24, "bold")).pack(pady=(20, 10), padx=40)
        
        email_entry = ctk.CTkEntry(login_frame, placeholder_text="Email Address", width=250)
        email_entry.pack(pady=10)
        pass_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*", width=250)
        pass_entry.pack(pady=10)
        
        error_label = ctk.CTkLabel(login_frame, text="", text_color="red")
        error_label.pack()

        def attempt_login():
            success, result = db_manager.verify_login(email_entry.get(), pass_entry.get())
            if success:
                self.current_user_id = result 
                self.build_main_dashboard()   
            else:
                error_label.configure(text=result)

        ctk.CTkButton(login_frame, text="Login", command=attempt_login, width=250).pack(pady=10)
        ctk.CTkButton(login_frame, text="Forgot Password?", fg_color="transparent", text_color="#3b82f6", command=self.show_forgot_password).pack()
        ctk.CTkButton(login_frame, text="Create an Account", fg_color="transparent", command=self.show_register_screen).pack(pady=(5, 20))

    # --- NEW: Forgot Password Flow ---
    def show_forgot_password(self):
        self.clear_screen()
        fp_frame = ctk.CTkFrame(self.container)
        fp_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(fp_frame, text="Reset Password", font=("Arial", 24, "bold")).pack(pady=(20, 10), padx=40)
        
        email_entry = ctk.CTkEntry(fp_frame, placeholder_text="Enter registered Email", width=250)
        email_entry.pack(pady=10)
        
        otp_entry = ctk.CTkEntry(fp_frame, placeholder_text="Enter 6-digit OTP", width=250)
        new_pass_entry = ctk.CTkEntry(fp_frame, placeholder_text="Enter New Password", show="*", width=250)
        
        error_label = ctk.CTkLabel(fp_frame, text="", text_color="red")
        error_label.pack(pady=5)
        
        self.generated_otp = None # Store the generated OTP

        def trigger_otp():
            email = email_entry.get()
            if not email:
                error_label.configure(text="Please enter your email.", text_color="red")
                return
            
            error_label.configure(text="Sending OTP...", text_color="white")
            self.update()
            
            success, result = db_manager.send_otp_email(email)
            if success:
                self.generated_otp = result
                error_label.configure(text="OTP Sent! Check terminal or email.", text_color="#10b981")
                email_entry.configure(state="disabled")
                send_otp_btn.pack_forget() # Hide the send button
                
                # Show the inputs for the next step
                otp_entry.pack(pady=5)
                new_pass_entry.pack(pady=5)
                reset_btn.pack(pady=15)
            else:
                error_label.configure(text="Failed to send OTP.", text_color="red")

        def reset_password():
            if otp_entry.get() == str(self.generated_otp):
                new_pwd = new_pass_entry.get()
                if len(new_pwd) > 3:
                    db_manager.update_password(email_entry.get(), new_pwd)
                    self.show_login_screen()
                else:
                    error_label.configure(text="Password too short.", text_color="red")
            else:
                error_label.configure(text="Invalid OTP code.", text_color="red")

        send_otp_btn = ctk.CTkButton(fp_frame, text="Send OTP", command=trigger_otp, width=250)
        send_otp_btn.pack(pady=10)
        
        reset_btn = ctk.CTkButton(fp_frame, text="Reset Password", command=reset_password, width=250)
        # reset_btn is packed dynamically after OTP is sent!
        
        ctk.CTkButton(fp_frame, text="Back to Login", fg_color="transparent", command=self.show_login_screen).pack(pady=(10, 20))

    def show_register_screen(self):
        self.clear_screen()
        reg_frame = ctk.CTkFrame(self.container)
        reg_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(reg_frame, text="Register New Account", font=("Arial", 24, "bold")).pack(pady=(20, 10), padx=40)
        
        email_entry = ctk.CTkEntry(reg_frame, placeholder_text="Email Address", width=250)
        email_entry.pack(pady=5)
        user_entry = ctk.CTkEntry(reg_frame, placeholder_text="Username", width=250)
        user_entry.pack(pady=5)
        pass_entry = ctk.CTkEntry(reg_frame, placeholder_text="Password", show="*", width=250)
        pass_entry.pack(pady=5)
        mobile_entry = ctk.CTkEntry(reg_frame, placeholder_text="Mobile Number", width=250)
        mobile_entry.pack(pady=5)
        
        error_label = ctk.CTkLabel(reg_frame, text="", text_color="red")
        error_label.pack()

        def attempt_register():
            u, p, e, m = user_entry.get(), pass_entry.get(), email_entry.get(), mobile_entry.get()
            if not e or not p:
                error_label.configure(text="Email and Password are required!")
                return
            success, msg = db_manager.register_user(u, p, e, m)
            if success: self.show_login_screen() 
            else: error_label.configure(text=msg)

        ctk.CTkButton(reg_frame, text="Register", command=attempt_register, width=250).pack(pady=15)
        ctk.CTkButton(reg_frame, text="Back to Login", fg_color="transparent", command=self.show_login_screen).pack(pady=(0, 20))

    # ==========================================
    # MAIN APPLICATION DASHBOARD
    # ==========================================
    def build_main_dashboard(self):
        self.clear_screen()
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(self.container, width=320)
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.task_label = ctk.CTkLabel(self.left_panel, text="My Pending Tasks", font=("Arial", 20, "bold"))
        self.task_label.pack(pady=10)

        self.btn_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.btn_frame.pack(pady=5)
        self.add_btn = ctk.CTkButton(self.btn_frame, text="ADD", width=80, command=self.add_task_gui)
        self.add_btn.grid(row=0, column=0, padx=5)
        self.modify_btn = ctk.CTkButton(self.btn_frame, text="MODIFY", width=80, command=self.modify_task_gui)
        self.modify_btn.grid(row=0, column=1, padx=5)
        self.delete_btn = ctk.CTkButton(self.btn_frame, text="DELETE", width=80, command=self.delete_task_gui, fg_color="#b23b3b", hover_color="#8c2e2e")
        self.delete_btn.grid(row=0, column=2, padx=5)

        ctk.CTkLabel(self.left_panel, text="Filter by Category:", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        self.filter_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.filter_frame.pack(pady=5)
        self.cat_work = ctk.CTkButton(self.filter_frame, text="Work", width=65, command=lambda: self.load_tasks("Work"))
        self.cat_work.grid(row=0, column=0, padx=5, pady=5)
        self.cat_personal = ctk.CTkButton(self.filter_frame, text="Personal", width=65, command=lambda: self.load_tasks("Personal"))
        self.cat_personal.grid(row=0, column=1, padx=5, pady=5)
        self.cat_family = ctk.CTkButton(self.filter_frame, text="Family", width=65, command=lambda: self.load_tasks("Family"))
        self.cat_family.grid(row=1, column=0, padx=5, pady=5)
        self.cat_health = ctk.CTkButton(self.filter_frame, text="Health", width=65, command=lambda: self.load_tasks("Health"))
        self.cat_health.grid(row=1, column=1, padx=5, pady=5)

        self.refresh_btn = ctk.CTkButton(self.left_panel, text="All Tasks / Refresh", command=self.load_tasks)
        self.refresh_btn.pack(pady=(10, 5))
        self.logout_btn = ctk.CTkButton(self.left_panel, text="Logout", command=self.logout, fg_color="#5a5a5a", hover_color="#3b3b3b")
        self.logout_btn.pack(pady=(0, 10))
        
        self.task_listbox = ctk.CTkTextbox(self.left_panel, width=300, height=450)
        self.task_listbox.pack(pady=5)

        self.right_panel = ctk.CTkFrame(self.container)
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.details_display = ctk.CTkTextbox(self.right_panel, state="disabled", font=("Arial", 14), wrap="word")
        self.details_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.input_frame = ctk.CTkFrame(self.right_panel)
        self.input_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.view_input = ctk.CTkEntry(self.input_frame, placeholder_text="Enter Task ID to view full description and AI Plan...")
        self.view_input.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.view_btn = ctk.CTkButton(self.input_frame, text="View Details", command=self.view_task_details, width=120)
        self.view_btn.grid(row=0, column=1, padx=10, pady=10)
        
        self.bind('<Return>', lambda event: self.view_task_details())
        self.load_tasks()

    def logout(self):
        self.current_user_id = None
        self.show_login_screen()

    def start_scheduler(self):
        def run_loop():
            while True:
                if self.current_user_id:
                    scheduler.check_for_reminders(self.current_user_id)
                time.sleep(60)
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()

    def load_tasks(self, category_filter="All"):
        self.task_listbox.configure(state="normal")
        self.task_listbox.delete("1.0", "end")
        tasks = db_manager.get_pending_tasks(self.current_user_id)
        if category_filter != "All":
            tasks = [t for t in tasks if t['category'] == category_filter]

        if not tasks:
            msg = "No pending tasks." if category_filter == "All" else f"No pending '{category_filter}' tasks."
            self.task_listbox.insert("end", f"{msg}\n")
        else:
            for t in tasks:
                self.task_listbox.insert("end", f"ID: {t['task_id']} | [{t['category']}] {t['title']}\nDue: {t['due_date']}\n{'-'*30}\n")
        self.task_listbox.configure(state="disabled")

    def view_task_details(self):
        task_id = self.view_input.get()
        if not task_id: return
        self.view_input.delete(0, "end")
        self.details_display.configure(state="normal")
        self.details_display.delete("1.0", "end")

        try:
            task_id_int = int(task_id)
            tasks = db_manager.get_pending_tasks(self.current_user_id)
            for t in tasks:
                if t['task_id'] == task_id_int:
                    header = f"Task: {t['title']}\nCategory: {t['category']}\nDue Date: {t['due_date']}\n"
                    header += "="*40 + "\n\n"
                    self.details_display.insert("end", header)
                    self.details_display.insert("end", f"{t['description']}\n")
                    self.details_display.configure(state="disabled")
                    return
            self.details_display.insert("end", "System: Task ID not found or task is completed.")
        except ValueError:
            self.details_display.insert("end", "System: Please enter a valid numerical ID.")
        self.details_display.configure(state="disabled")

    # ==========================================
    # GUI Popup Functions
    # ==========================================
    def add_task_gui(self):
        add_window = ctk.CTkToplevel(self)
        add_window.title("Create New Task")
        add_window.geometry("420x750")
        add_window.attributes("-topmost", True)

        ctk.CTkLabel(add_window, text="Task Title:", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        title_entry = ctk.CTkEntry(add_window, width=320)
        title_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Brief Description:", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        desc_entry = ctk.CTkTextbox(add_window, width=320, height=60, wrap="word")
        desc_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Category:", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        category_var = ctk.StringVar(value="Work")
        category_menu = ctk.CTkComboBox(add_window, values=["Personal", "Family", "Work", "Health"], variable=category_var, width=150)
        category_menu.pack(pady=5)

        ctk.CTkLabel(add_window, text="Due Date:", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        cal = Calendar(add_window, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=5)

        time_frame = ctk.CTkFrame(add_window, fg_color="transparent")

        hour_var = ctk.StringVar(value="12")
        hour_menu = ctk.CTkComboBox(time_frame, values=[f"{i:02d}" for i in range(1, 13)], variable=hour_var, width=70)
        hour_menu.grid(row=0, column=0, padx=5)
        ctk.CTkLabel(time_frame, text=":", font=("Arial", 14, "bold")).grid(row=0, column=1)
        minute_var = ctk.StringVar(value="00")
        minute_menu = ctk.CTkComboBox(time_frame, values=[f"{i:02d}" for i in range(0, 60, 5)], variable=minute_var, width=70)
        minute_menu.grid(row=0, column=2, padx=5)
        ampm_var = ctk.StringVar(value="PM")
        ampm_menu = ctk.CTkComboBox(time_frame, values=["AM", "PM"], variable=ampm_var, width=70)
        ampm_menu.grid(row=0, column=3, padx=5)

        use_ai_var = ctk.BooleanVar(value=False) 
        ai_checkbox = ctk.CTkCheckBox(add_window, text="USE AI: Generate a step-by-step plan", variable=use_ai_var, font=("Arial", 12, "bold"), fg_color="#2b8256")
        ai_checkbox.pack(pady=15)

        def save_new_task():
            title = title_entry.get()
            user_desc = desc_entry.get("1.0", "end-1c").strip()
            category = category_var.get()
            date_str = cal.get_date()
            hr = int(hour_var.get())
            if ampm_var.get() == "PM" and hr != 12: hr += 12
            elif ampm_var.get() == "AM" and hr == 12: hr = 0
            
            time_str = f"{hr:02d}:{minute_var.get()}:00"
            due_datetime = f"{date_str} {time_str}"
            
            if not title:
                title_entry.configure(placeholder_text="Title REQUIRED!", border_color="red")
                return

            final_description = user_desc
            if use_ai_var.get():
                save_btn.configure(text="Generating Plan... Please Wait", state="disabled")
                add_window.update() 
                ai_plan = ai_brain.generate_task_plan(title, user_desc)
                final_description = f"User Note: {user_desc}\n\n--- AI GENERATED PLAN ---\n{ai_plan}" if user_desc else f"--- AI GENERATED PLAN ---\n{ai_plan}"
            
            db_manager.add_task(title, final_description, category, due_datetime, self.current_user_id)
            self.load_tasks()
            add_window.destroy() 

        save_btn = ctk.CTkButton(add_window, text="Save Task", command=save_new_task, font=("Arial", 14, "bold"))
        save_btn.pack(pady=10)

    def modify_task_gui(self):
        dialog_id = ctk.CTkInputDialog(text="Enter the ID of the task to modify:", title="Modify Task")
        task_id = dialog_id.get_input()
        if task_id:
            try:
                task_id_int = int(task_id)
                dialog_title = ctk.CTkInputDialog(text="Enter the NEW title for this task:", title="New Task Title")
                new_title = dialog_title.get_input()
                if new_title:
                    db_manager.update_task_title(task_id_int, new_title)
                    self.load_tasks()
            except ValueError:
                self.details_display.configure(state="normal")
                self.details_display.insert("end", "\nSystem Error: Please enter a valid ID.")
                self.details_display.configure(state="disabled")

    def delete_task_gui(self):
        dialog = ctk.CTkInputDialog(text="Enter the ID of the task to delete:", title="Delete Task")
        task_id = dialog.get_input()
        if task_id:
            try:
                task_id_int = int(task_id)
                db_manager.delete_task(task_id_int)
                self.load_tasks()
                self.details_display.configure(state="normal")
                self.details_display.delete("1.0", "end")
                self.details_display.configure(state="disabled")
            except ValueError:
                self.details_display.configure(state="normal")
                self.details_display.insert("end", "\nSystem Error: Please enter a valid ID.")
                self.details_display.configure(state="disabled")

if __name__ == "__main__":
    app = AITaskManager()
    app.mainloop()
