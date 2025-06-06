import MySQLdb
from webapp import mysql
from flask_mysqldb import MySQL
from flask import request, session, redirect, url_for, flash

class auth:
    @staticmethod
    def signup(email,generate_password_hash,password):
        if not email or not password:
            flash("Please fill in all fields", "danger")
            return redirect(url_for("controller.signup"))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            with mysql.connection.cursor() as cur:
                cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
                mysql.connection.commit()
                flash("Sign Up Successful!", "success")
        except Exception as e:
            print("Database Error:", e)
            flash("An error occurred. Please try again.", "danger")
            cur.close()
            return hashed_password
        
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
