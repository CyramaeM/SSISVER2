import MySQLdb
from webapp import mysql
from flask_mysqldb import MySQL
from flask import  flash


class Course:
    @staticmethod
    def get_by_code(code):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use DictCursor
        query = "SELECT * FROM course WHERE coursecode = %s"
        cur.execute(query, (code,))
        result = cur.fetchone()
        cur.close()
        return result
        
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
                college.collegename 
            FROM 
                course 
            LEFT JOIN 
                college 
            ON 
                course.collegebelong = college.collegecode
        """)
        courses = cur.fetchall()
        cur.close()
        return courses

    
    @staticmethod
    def add_course(course_code, course_name, college_belong):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # ✅ Check if the course already exists
        cursor.execute("SELECT coursecode FROM course WHERE coursecode = %s", (course_code,))
        existing_course = cursor.fetchone()

        if existing_course:
            if existing_course.get('deleted') is not None:  # ✅ Reactivate deleted course
                cursor.execute("""
                    UPDATE course SET deleted = NULL, coursename = %s, collegebelong = %s WHERE coursecode = %s
                """, (course_name, college_belong, course_code))
                mysql.connection.commit()
                cursor.close()
                flash("Course reactivated successfully!", "success")
                return True
            else:
                flash("Course code already exists. Please try another.", "danger")
                return False  # ❌ Prevent duplicate entry

        # ✅ Insert new course if it doesn't exist
        try:
            cursor.execute("""
                INSERT INTO course (coursecode, coursename, collegebelong)
                VALUES (%s, %s, %s)
            """, (course_code, course_name, college_belong))

            mysql.connection.commit()
            cursor.close()
            flash("Course added successfully!", "success")
            return True

        except Exception as e:
            print("Database Error:", e)
            flash("An error occurred. Please try again.", "danger")
            return False
            
    @staticmethod
    def edit_course(coursecode, course_name, college_belong=None):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            # Update both course name and college
            cursor.execute("""
                UPDATE course
                SET coursename = %s, collegebelong = %s
                WHERE coursecode = %s
            """, (course_name, college_belong, coursecode))

            mysql.connection.commit()
            cursor.close()
            return True  # Success

        except Exception as e:
            print("Database Error:", e)
            flash("Error updating course. Please try again.", "danger")
            return False

    @staticmethod
    def delete_course(course_code):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        try:
            # ✅ Step 1: Check if students are enrolled in the course
            cursor.execute("SELECT COUNT(*) AS student_count FROM students WHERE course = %s", (course_code,))
            student_count = cursor.fetchone()["student_count"]

            # ✅ Step 3: Proceed with deletion if no students are enrolled
            cursor.execute("UPDATE students SET course = NULL WHERE course = %s", (course_code,))
            cursor.execute("DELETE FROM course WHERE coursecode = %s", (course_code,))
            mysql.connection.commit()
            cursor.close()
            flash("Course deleted successfully!", "success")
            return True

        except Exception as e:
            print("Database Error:", e)  # Debugging
            flash("Error processing course deletion. Please try again.", "danger")
            return False


