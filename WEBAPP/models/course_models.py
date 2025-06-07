import MySQLdb
from webapp import mysql
from flask_mysqldb import MySQL
from flask import  flash


class Course:

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM course")  # ✅ Ensure correct table name
        courses = cur.fetchall()
        cur.close()
        return courses
        
    @staticmethod
    def coursehome():
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            SELECT 
                course.coursecode, 
                course.coursename, 
                course.collegebelong, 
                college.collegecode, 
                college.collegename 
            FROM 
                course 
            JOIN 
                college 
            ON 
                course.collegebelong = college.collegecode
        """)
        
        courses = cur.fetchall()
        cur.close()  # ✅ Close the cursor
        
        return courses  # ✅ Return the retrieved data

    
    @staticmethod
    def add_course(course_code, course_name, college_belong):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # ✅ Step 1: Check if the course code already exists
        cursor.execute("SELECT coursecode FROM course WHERE coursecode = %s", (course_code,))
        existing_course = cursor.fetchone()

        if existing_course:
            flash("Course code already exists. Please try another.", "danger")
            return False  # ❌ Prevent duplicate entry

        # ✅ Step 2: Insert into the database if it doesn't exist
        try:
            cursor.execute("""
                INSERT INTO course (coursecode, coursename, collegebelong)
                VALUES (%s, %s, %s)
            """, (course_code, course_name, college_belong))

            mysql.connection.commit()
            cursor.close()
            flash("Course added successfully!", "success")
            return True  # ✅ Return success flag

        except Exception as e:
            print("Database Error:", e)  # Debugging
            flash("An error occurred. Please try again.", "danger")
            return False  # ❌ Handle failure gracefully


    @staticmethod
    def edit_course(coursecode, course_name):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute("""
                UPDATE course
                SET coursename = %s
                WHERE coursecode = %s
            """, (course_name, coursecode))  # ✅ Ensure correct parameter order

            mysql.connection.commit()
            cursor.close()
            flash("Course updated successfully!", "success")
            return True  # ✅ Return success flag

        except Exception as e:
            print("Database Error:", e)  # Debugging
            flash("Error updating course. Please try again.", "danger")
            return False  # ❌ Handle failure gracefully


    @staticmethod
    def delete_course(course_code):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute("DELETE FROM course WHERE coursecode = %s", (course_code,))
            mysql.connection.commit()
            cursor.close()
            flash("Course deleted successfully!", "success")
            return True  # ✅ Return success flag
        except Exception as e:
            print("Database Error:", e)  # Debugging
            flash("Error deleting course. Please try again.", "danger")
            return False  # ❌ Handle failure gracefully
