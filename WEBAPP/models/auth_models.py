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
    def login(email,check_password_hash,password,hashed_password,user_id):
        if request.method == "POST":
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  
            cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            print("Fetched user:", user)

            if not user:
                flash("Invalid email or password", "danger")

            if check_password_hash(hashed_password, password):  
                session["user_id"] = user_id
                flash("Login successful!", "success")
        
            else:
                flash("Invalid email or password", "danger")

    
    @staticmethod
    def logout():
        session.pop('user_id', None) 
        flash("You have been logged out.", "info")
