from flask import render_template, url_for, redirect, request, flash, Blueprint
from flask_login import login_required
from flask_wtf.csrf import generate_csrf
import MySQLdb
import cloudinary
import cloudinary.uploader
import re
from webapp.controller import login
from webapp.models.student_models import student

student_bp = Blueprint('students', __name__, template_folder='templates')


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@student_bp.route('/students', methods=['GET'])
def student_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_students = student.get_total_students()
    total_pages = max((total_students // per_page) + (1 if total_students % per_page > 0 else 0), 1)
    students = student.get_students(page, per_page)
    
    # Get course details for formatting
    course_details = student.get_course_details()
    
    return render_template('student.html', 
                           students=students, 
                           page=page, 
                           total_pages=total_pages,
                           course_details=course_details)


@student_bp.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    total_pages, students = student.fetch_student(per_page, offset)
    
    # Get course details for formatting
    course_details = student.get_course_details()
    
    return render_template('student.html', 
                           page=page, 
                           total_pages=total_pages, 
                           students=students,
                           course_details=course_details)

@student_bp.route('/addstudent', methods=['GET', 'POST'])
def add_student():
    if request.method == 'GET':
        # Get course details for dropdown
        course_details = student.get_course_details()
        return render_template('add_student.html', course_details=course_details)
    
    # Retrieve form data
    stud_id = request.form.get('stud_id', '').strip()
    fname = request.form.get('fname', '').strip()
    lname = request.form.get('lname', '').strip()
    course = request.form.get('course', '').strip()
    yearlevel = request.form.get('yearlevel', '').strip()
    gender = request.form.get('gender', '').strip()
    profile_photo = request.files.get('profile_photo')
    
    # Validate required fields
    if not stud_id or not fname or not lname or not course:
        flash("All fields are required!", "error")
        return redirect(url_for('students.add_student'))
    
    # Check for duplicate student ID
    if student.student_exists(stud_id):
        flash("A student with that ID number already exists!", "error")
        return redirect(url_for('students.add_student'))
    
    # Handle profile photo upload to Cloudinary
    photo_url = None
    photo_public_id = None
    
    if profile_photo and profile_photo.filename != '':
        try:
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                profile_photo,
                folder="student_profiles/"
            )
            photo_url = upload_result['secure_url']
            photo_public_id = upload_result['public_id']
        except Exception as e:
            print("Cloudinary Upload Error:", e)
            flash("Error uploading profile photo. Student added without photo.", "warning")
    
    try:
        student.add_student(stud_id, fname, lname, course, yearlevel, gender, photo_url, photo_public_id)
        flash("Student added successfully!", "success")
    except MySQLdb.IntegrityError as e:
        # Handle duplicate entry specifically
        print("Database Integrity Error:", e)
        flash("A student with that ID number already exists!", "error")
    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred while adding the student. Try again.", "error")
    
    return redirect(url_for('students.home'))

@student_bp.route('/edit_student/<string:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    # Get course details for dropdown
    course_details = student.get_course_details()
    
    if request.method == 'POST':
        fname = request.form.get('fname', '').strip()
        lname = request.form.get('lname', '').strip()
        course = request.form.get('course', '').strip()
        yearlevel = request.form.get('yearlevel', '').strip()
        gender = request.form.get('gender', '').strip()
        profile_photo = request.files.get('profile_photo')
        remove_photo = request.form.get('remove_photo') == 'on'

        if not all([fname, lname, course, yearlevel, gender]):
            flash("All fields are required!", "danger")
            return redirect(url_for('students.edit_student', student_id=student_id))

        try:
            # Handle profile photo changes
            photo_url = None
            photo_public_id = None
            
            # Get current student data to check existing photo
            current_student = student.get_student_by_id(student_id)
            
            if profile_photo and profile_photo.filename != '':
                # Upload new photo to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    profile_photo,
                    folder="student_profiles/"
                )
                photo_url = upload_result['secure_url']
                photo_public_id = upload_result['public_id']
                
                # Delete old photo if exists
                if current_student and current_student.get('profile_id'):
                    try:
                        cloudinary.uploader.destroy(current_student['profile_id'])
                    except Exception as e:
                        print("Error deleting old profile photo:", e)
            elif remove_photo:
                # Delete existing photo
                if current_student and current_student.get('profile_id'):
                    try:
                        cloudinary.uploader.destroy(current_student['profile_id'])
                    except Exception as e:
                        print("Error deleting profile photo:", e)
            else:
                # Keep existing photo if not changing
                if current_student:
                    photo_url = current_student.get('profile')
                    photo_public_id = current_student.get('profile_id')

            # Update student with new data and photo
            student.edit_student(
                student_id, 
                fname, 
                lname, 
                course, 
                yearlevel, 
                gender, 
                photo_url, 
                photo_public_id
            )
            
            flash("Student updated successfully!", "success")
            return redirect(url_for('students.home'))
        except Exception as e:
            print("Error updating student:", e)
            flash("Error updating student. Please try again.", "danger")
            return redirect(url_for('students.edit_student', student_id=student_id))

    # GET request - fetch data for form
    student_data = student.get_student_by_id(student_id.strip())
    
    if not student_data:
        flash("Student not found!", "danger")
        return redirect(url_for('students.home'))

    return render_template("edit_student.html", 
                           student=student_data, 
                           courses=course_details,
                           year_levels=['1', '2', '3', '4'],
                           genders=['Male', 'Female', 'Other'],
                           csrf_token=generate_csrf())
                           
@student_bp.route('/delete_student/<string:student_id>', methods=['POST'])
def delete_student(student_id):
    student.delete_student(student_id)
    return redirect(url_for('students.home'))
