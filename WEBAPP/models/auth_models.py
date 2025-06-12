import MySQLdb
from webapp import mysql
from flask_mysqldb import MySQL
from flask import request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash,generate_password_hash

class auth:
    @staticmethod
    def get_user_by_email(email):
        """Fetch user details by email."""
        with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cur:
            cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
        return user
    
    @staticmethod
    def login(email, password):
        """Authenticate user and store session."""
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        
        print("Fetched user:", user)  # ✅ Debugging

        if not user:
            flash("Invalid email or password", "danger")
            return False  # ❌ Return failure so the route can handle it

        if check_password_hash(user['password'], password):  # ✅ Compare hashed password
            session["user_id"] = user["id"]
            flash("Login successful!", "success")
            return True  # ✅ Return success flag
        
        flash("Invalid email or password", "danger")
        return False  # ❌ Ensure login fails properly


    @staticmethod
    def signup(email, password):
        """Insert new user into the database."""
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            with mysql.connection.cursor() as cur:
                cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
                mysql.connection.commit()
                return True  # Successfully created user
        except Exception as e:
            print("Database Error:", e)
            return False  # Failed to create user
    
    @staticmethod
    def logout():
        session.pop('user_id', None) 
        flash("You have been logged out.", "info")
