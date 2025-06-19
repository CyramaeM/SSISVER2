import MySQLdb
from webapp import mysql
from flask_mysqldb import MySQL
from flask import  flash


class Course:
    @staticmethod
    def get_by_code(code):
        from webapp.database import mysql
        cur = mysql.connection.cursor()
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
            return True  # ✅ Return success flag

        except Exception as e:
            print("Database Error:", e)  # Debugging
            flash("Error updating course. Please try again.", "danger")
            return False  # ❌ Handle failure gracefully


    @staticmethod
    def delete_course(course_code):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        try:
            # ✅ Step 1: Check if students are enrolled in the course
            cursor.execute("SELECT COUNT(*) AS student_count FROM students WHERE coursecode = %s", (course_code,))
            student_count = cursor.fetchone()["student_count"]

            if student_count > 0:  # ❌ Prevent deletion if students are enrolled
                flash("Cannot delete course. Students are enrolled in it.", "danger")
                cursor.close()
                return False

            # ✅ Step 2: Proceed with deletion if no students are enrolled
            cursor.execute("DELETE FROM course WHERE coursecode = %s", (course_code,))
            mysql.connection.commit()
            cursor.close()
            flash("Course deleted successfully!", "success")
            return True

        except Exception as e:
            print("Database Error:", e)  # Debugging
            flash("Error deleting course. Please try again.", "danger")
            return False

