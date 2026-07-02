AI Task ManagerAn intelligent, full-stack task management application that leverages AI to optimize productivity.

DescriptionThis project is a full-stack Python-based AI Task Manager that integrates real-time Gemini-powered intelligent planning, secure OTP-based authentication, and automated background deadline notifications using a MySQL backend.  

Key Technical Features:

AI-Driven Planning: Uses ai_brain.py and the Gemini API to transform user tasks into structured, actionable checklists.  Secure Authentication: Implements db_manager.py for email-based login and a robust OTP (One-Time Password) flow for secure account recovery.  
Real-Time Notifications: Features a multi-threaded scheduler (scheduler.py) that monitors upcoming deadlines and triggers OS-level alerts via the plyer library.  
Modern UI: Built with CustomTkinter to provide a high-performance, cross-platform graphical interface with light/dark mode support. 
Database Infrastructure: Manages persistent data using MySQL, with utility scripts (setup_db.py, reset_db.py) to handle relational schema integrity and lifecycle state management.  

Prerequisites:
To run this project, you will need:
Python 3.xMySQL ServerRequired libraries: mysql-connector-python, customtkinter, tkcalendar, plyer, google-genai
