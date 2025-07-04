import MySQLdb
from webapp.database import mysql
from flask import  flash
import cloudinary


class student:
    def get_students(page, per_page=10):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        offset = (page - 1) * per_page
        # Updated query to join with course table
        cursor.execute("""
            SELECT s.*, c.coursename 
            FROM students s
            LEFT JOIN course c ON s.course = c.coursecode
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        
        students = cursor.fetchall()
        cursor.close()
        return students

    @staticmethod
    def get_total_students():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) AS total FROM students")
        result = cursor.fetchone()
        cursor.close()
        
        return result["total"] if result else 0  # ✅ Return total student count safely


    @staticmethod
    def fetch_student(per_page=10, offset=0):
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            # Updated query to join with course table
            cur.execute("""
                SELECT s.*, c.coursename 
                FROM students s
                LEFT JOIN course c ON s.course = c.coursecode
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            students = cur.fetchall()
            
            # Get total student count
            cur.execute("SELECT COUNT(*) AS total FROM students")
            total_students = cur.fetchone()['total']
            cur.close()
            
            total_pages = max(1, (total_students + per_page - 1) // per_page)  
            return total_pages, students
            
        except Exception as e:
            print(f"Database Error in home(): {e}")
            flash("Failed to load student list", "danger")
            return 1, []

    @staticmethod
    def get_course_details():
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT coursecode, coursename FROM course")  
        courses = {row['coursecode']: row['coursename'] for row in cur.fetchall()}
        cur.close()
        return courses

    @staticmethod
    def get_courses():
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT coursecode FROM course")  
        courses = [row['coursecode'] for row in cur.fetchall()]
        cur.close()
        return courses
    
    @staticmethod
    def get_by_id(student_id):
        from webapp.database import mysql
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE id_number = %s", (student_id,))
        row = cur.fetchone()
        if row is None:
            cur.close()
            return None
        columns = [col[0] for col in cur.description]
        result = dict(zip(columns, row))
        cur.close()
        return result

    @staticmethod
    def student_exists(stud_id):
        """Check if a student with given ID already exists"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT 1 FROM students WHERE id_number = %s", (stud_id,))
            exists = cur.fetchone() is not None
            cur.close()
            return exists
        except Exception as e:
            print("Error checking student existence:", e)
            return False  # Assume exists to prevent duplicates            

    @staticmethod
    def add_student(stud_id, fname, lname, course, yearlevel, gender, photo_url, photo_public_id):
        try:
            with mysql.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO students (id_number, fname, lname, course, yearlevel, gender, profile, profile_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (stud_id, fname, lname, course, yearlevel, gender, photo_url, photo_public_id))
                mysql.connection.commit()
                return True
        except MySQLdb.IntegrityError as e:
            # Duplicate entry error
            print("Integrity Error:", e)
            mysql.connection.rollback()
            raise e  # Re-raise to handle in controller
        except Exception as e:
            print("Database Error:", e)
            mysql.connection.rollback()
            raise e  # Re-raise to handle in controller

    @staticmethod
    def get_student_by_id(student_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM students WHERE id_number = %s", (student_id,))
        student_data = cur.fetchone()
        cur.close()
        return student_data

    @staticmethod
    def edit_student(id_number, fname, lname, course, yearlevel, gender):
        from webapp.database import mysql
        import MySQLdb.cursors

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            UPDATE students 
            SET fname=%s, lname=%s, course=%s, yearlevel=%s, gender=%s 
            WHERE id_number=%s
        """, (fname, lname, course, yearlevel, gender, id_number))
        mysql.connection.commit()
        row_count = cur.rowcount
        cur.close()
        return row_count > 0  # Return True if a row was updated



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