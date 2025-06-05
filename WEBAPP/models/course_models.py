import MySQLdb
from webapp import mysql
from flask_mysqldb import MySQL
from flask import  flash


class course:
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
        cur.commit()
        cur.close()
        return courses
    
    @staticmethod
    def add_course(course_code,course_name,college_belong):
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.exceute("""
                INSERT INTO course (coursecode, coursename, collegebelong)
                VALUES (%s, %s, %s)
            """, (course_code, course_name, college_belong))
        mysql.connection.commit()
        flash("Course added successfully!", "success")
        cursor.close()

    @staticmethod
    def edit_course(course_code,course_name,coursecode):
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
                UPDATE course
                SET coursecode = %s, coursename = %s
                WHERE coursecode = %s
            """, (course_code, course_name, coursecode)) 

        mysql.connection.commit()
        flash("Course updated successfully!", "success")
        cursor.close()

    @staticmethod
    def delete_course(coursecode):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("DELETE FROM course WHERE coursecode = %s", (coursecode,))
        mysql.connection.commit()
        flash("Course deleted successfully!", "success")
        cur.close()