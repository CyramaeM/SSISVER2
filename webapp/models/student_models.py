import MySQLdb
from webapp.database import mysql
from flask import  flash
import cloudinary

COLUMN_MAP = {
    'id_number': 's.id_number',
    'fname': 's.fname',
    'lname': 's.lname',
    'coursename': 'c.coursename',
    'yearlevel': 's.yearlevel'
}    

class student:

    @staticmethod
    def fetch_student(per_page=10, offset=0, sort_by='id_number', sort_dir='ASC'):
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            # Validate and map sorting parameters
            db_column = COLUMN_MAP.get(sort_by, 's.id_number')
            sort_dir = 'ASC' if sort_dir.upper() not in ['ASC', 'DESC'] else sort_dir.upper()

            query = f"""
                SELECT s.*, c.coursename 
                FROM students s
                LEFT JOIN course c ON s.course = c.coursecode
                ORDER BY {db_column} {sort_dir}
                LIMIT %s OFFSET %s
            """
            cur.execute(query, (per_page, offset))
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
    def get_total_students():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) AS total FROM students")
        result = cursor.fetchone()
        cursor.close()
        
        return result["total"] if result else 0  # ✅ Return total student count safely


    @staticmethod
    def fetch_student(per_page=10, offset=0, sort_by='id_number', sort_dir='ASC'):
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            # Validate and map sorting parameters
            db_column = COLUMN_MAP.get(sort_by, 's.id_number')
            sort_dir = 'ASC' if sort_dir.upper() not in ['ASC', 'DESC'] else sort_dir.upper()

            query = f"""
                SELECT s.*, c.coursename 
                FROM students s
                LEFT JOIN course c ON s.course = c.coursecode
                ORDER BY {db_column} {sort_dir}
                LIMIT %s OFFSET %s
            """
            cur.execute(query, (per_page, offset))
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

    def edit_student(id_number, fname, lname, course, yearlevel, gender, 
                    photo_url=None, photo_public_id=None):
        try:
            with mysql.connection.cursor() as cur:
                # Update with photo fields
                cur.execute("""
                    UPDATE students 
                    SET fname=%s, lname=%s, course=%s, yearlevel=%s, 
                        gender=%s, profile=%s, profile_id=%s
                    WHERE id_number=%s
                """, (
                    fname, lname, course, yearlevel, gender, 
                    photo_url, photo_public_id, id_number
                ))
                mysql.connection.commit()
                return True
        except Exception as e:
            print("Database Error:", e)
            raise e
            
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
    def search(query, per_page=10, offset=0, sort_by='id_number', sort_dir='ASC'):
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            like_query = f"%{query}%"

            # Validate and map sorting parameters
            db_column = COLUMN_MAP.get(sort_by, 's.id_number')
            sort_dir = 'ASC' if sort_dir.upper() not in ['ASC', 'DESC'] else sort_dir.upper()

            # Determine if query is a yearlevel filter
            is_yearlevel = query.isdigit() and query in ['1', '2', '3', '4']  # Adjust as needed

            if is_yearlevel:
                # Filter strictly by yearlevel
                cur.execute("""
                    SELECT COUNT(*) AS total 
                    FROM students s
                    LEFT JOIN course c ON s.course = c.coursecode
                    WHERE s.yearlevel = %s
                """, (query,))
                total_results = cur.fetchone()["total"]

                query_str = f"""
                    SELECT s.*, c.coursename 
                    FROM students s
                    LEFT JOIN course c ON s.course = c.coursecode
                    WHERE s.yearlevel = %s
                    ORDER BY {db_column} {sort_dir}
                    LIMIT %s OFFSET %s
                """
                cur.execute(query_str, (query, per_page, offset))

            else:
                # General fuzzy search across fields
                cur.execute("""
                    SELECT COUNT(*) AS total 
                    FROM students s
                    LEFT JOIN course c ON s.course = c.coursecode
                    WHERE s.id_number LIKE %s
                        OR s.fname LIKE %s
                        OR s.lname LIKE %s
                        OR s.course LIKE %s
                        OR c.coursename LIKE %s
                        OR s.gender = %s
                """, (like_query, like_query, like_query, like_query, like_query, query))

                total_results = cur.fetchone()["total"]

                query_str = f"""
                    SELECT s.*, c.coursename 
                    FROM students s
                    LEFT JOIN course c ON s.course = c.coursecode
                    WHERE s.id_number LIKE %s
                        OR s.fname LIKE %s
                        OR s.lname LIKE %s
                        OR s.course LIKE %s
                        OR c.coursename LIKE %s
                        OR s.gender = %s
                    ORDER BY {db_column} {sort_dir}
                    LIMIT %s OFFSET %s
                """
                cur.execute(query_str, (
                    like_query, like_query, like_query,
                    like_query, like_query, query,
                    per_page, offset
                ))

            results = cur.fetchall()
            cur.close()

        except Exception as e:
            print("Database Error:", e)
            flash("An error occurred while searching. Please try again.", "danger")
            total_results = 0
            results = []

        total_pages = max(1, (total_results + per_page - 1) // per_page)
        return total_pages, results

