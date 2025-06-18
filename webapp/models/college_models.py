from sqlite3 import Cursor
import MySQLdb
from webapp import mysql
from flask_mysqldb import MySQL
from flask import request, session, redirect, url_for, flash


class College:
    @staticmethod
    def get_by_code(college_code):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT collegecode, collegename FROM college WHERE collegecode = %s", (college_code,))
        college = cur.fetchone()
        cur.close()
        return college
    
    @staticmethod
    def collegehome():
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT collegecode, collegename FROM college")
        colleges = cur.fetchall()
        cur.close()
        return colleges
    
    @staticmethod
    def get_all_colleges():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT collegecode, collegename FROM college")
        colleges = cursor.fetchall()
        cursor.close()
        return colleges  # ✅ Return list of colleges
    
    @staticmethod
    def add_college(collegecode, collegename):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # ✅ Step 1: Check if the college code already exists
        cur.execute("SELECT collegecode FROM college WHERE collegecode = %s", (collegecode,))
        existing_college = cur.fetchone()

        if existing_college:
            flash("College code already exists. Please try another.", "danger")
            return False  # ❌ Prevent duplicate entry

        # ✅ Step 2: Insert into the database if it doesn't exist
        try:
            cur.execute("INSERT INTO college (collegecode, collegename) VALUES (%s, %s)", (collegecode, collegename))
            mysql.connection.commit()
            flash("College added successfully!", "success")
        except Exception as e:
            print("Database Error:", e)  # Debugging
            flash("An error occurred. Please try again.", "danger")
        
        cur.close()
        return True

       
    @staticmethod
    def edit_college(college_code, college_name):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute("""
                UPDATE college
                SET collegename = %s
                WHERE collegecode = %s
            """, (college_name, college_code))

            mysql.connection.commit()
            cursor.close()
            flash("College updated successfully!", "success")
            return True  # ✅ Return success flag

        except Exception as e:
            print("Database Error:", e)  # ✅ Print debugging info
            flash("Error updating college. Please try again.", "danger")
            return False  # ❌ Return failure flag



    @staticmethod
    def delete_college(college_code):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        try:
            # ✅ Step 1: Check if students are enrolled in courses belonging to this college
            cursor.execute("""
                SELECT COUNT(*) AS student_count 
                FROM students s 
                JOIN course c ON s.coursecode = c.coursecode 
                WHERE c.collegebelong = %s
            """, (college_code,))
            
            student_count = cursor.fetchone()["student_count"]

            if student_count > 0:  # ❌ Prevent deletion if students are enrolled
                flash("Cannot delete college. Students are still enrolled in its courses.", "danger")
                cursor.close()
                return False

            # ✅ Step 2: Proceed with deletion if no students are enrolled
            cursor.execute("DELETE FROM college WHERE collegecode = %s", (college_code,))
            mysql.connection.commit()
            cursor.close()
            flash("College deleted successfully!", "success")
            return True

        except Exception as e:
            print("Database Error:", e)  # Debugging
            flash("Error deleting college. Please try again.", "danger")
            return False
