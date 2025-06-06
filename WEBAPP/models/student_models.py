import MySQLdb
from webapp.database import mysql
from flask import  flash
import cloudinary


class student:
    @staticmethod
    def fetch_student(per_page=10, offset=0):
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            # Get paginated students
            cur.execute("SELECT * FROM students LIMIT %s OFFSET %s", (per_page, offset))
            students = cur.fetchall()
            
            # Get total student count
            cur.execute("SELECT COUNT(*) AS total FROM students")
            total_students = cur.fetchone()['total']
            cur.close()  # Close cursor AFTER both queries
            
            # Handle zero students case
            total_pages = max(1, (total_students + per_page - 1) // per_page)  
            
            return total_pages, students
            
        except Exception as e:
            print(f"Database Error in home(): {e}")
            flash("Failed to load student list", "danger")
            return 1, []  # Return safe defaults

    @staticmethod
    def get_courses():
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT coursecode FROM course")  
        courses = [row['coursecode'] for row in cur.fetchall()]
        cur.close()
        return courses

    @staticmethod
    def add_student(stud_id, fname, lname, course, yearlevel, gender, photo_url, photo_public_id):
        try:
            with mysql.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO students (id_number, fname, lname, course, yearlevel, gender, profile, profile_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (stud_id, fname, lname, course, yearlevel, gender, photo_url, photo_public_id))
                
                mysql.connection.commit()
        except Exception as e:
            print("Database Error:", e)
            flash("An error occurred while saving student data.", "danger")

    @staticmethod
    def get_student_by_id(student_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM students WHERE id_number = %s", (student_id,))
        student_data = cur.fetchone()
        cur.close()
        return student_data

    
    @staticmethod
    def edit_student(id_number, fname, lname, course, yearlevel, gender):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            UPDATE students 
            SET fname=%s, lname=%s, course=%s, yearlevel=%s, gender=%s 
            WHERE id_number=%s
        """, (fname, lname, course, yearlevel, gender, id_number))  # ✅ Fix argument order

        mysql.connection.commit()  # ✅ Commit changes
        cur.close()


    @staticmethod
    def delete_student(student_id):
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cur.execute("SELECT profile_id FROM students WHERE id_number = %s", (student_id,))
            student = cur.fetchone()
            profile_public_id = student.get('profile_id') if student else None

        
            cur.execute("DELETE FROM students WHERE id_number = %s", (student_id,))
            mysql.connection.commit()
            cur.close()

    
            if profile_public_id:
                cloudinary.uploader.destroy(profile_public_id)

            flash("Student deleted successfully!", "success")
        except Exception as e:
            print("Database Error:", e)
            flash("An error occurred. Please try again.", "danger")

    @staticmethod
    def search(query,per_page=10,offset=0):
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("""
                SELECT COUNT(*) AS total FROM students
                WHERE id_number = %s
                OR fname LIKE %s
                OR lname LIKE %s
                OR course LIKE %s
                OR gender = %s
                OR yearlevel = %s
            """, (query, f"%{query}%", f"%{query}%", f"%{query}%", query, query))
            
            total_results = cur.fetchone()["total"]
            cur.execute("""
                SELECT id_number, fname, lname, course, yearlevel, gender, profile
                FROM students
                WHERE id_number = %s
                OR fname LIKE %s
                OR lname LIKE %s
                OR course LIKE %s
                OR gender = %s
                OR yearlevel = %s
                LIMIT %s OFFSET %s
            """, (query, f"%{query}%", f"%{query}%", f"%{query}%", query, query, per_page, offset))
            results = cur.fetchall()
            cur.close()
        except Exception as e:
            print("Database Error:", e)
            flash("An error occurred while searching. Please try again.", "danger")

        total_pages = (total_results + per_page - 1) // per_page
        return total_pages,results 