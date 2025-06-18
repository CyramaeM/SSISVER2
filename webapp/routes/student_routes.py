from flask import render_template, url_for, redirect, request, flash, Blueprint
from flask_login import login_required
import MySQLdb
import cloudinary
import re
from webapp.controller import login
from webapp.models.student_models import student

student_bp = Blueprint('students', __name__, template_folder='templates')


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@student_bp.route('/students', methods=['GET'])
def student_list():
    page = request.args.get('page', 1, type=int)  # ✅ Get page number from URL query
    per_page = 10  # ✅ Number of students per page

    total_students = student.get_total_students()  # ✅ Get total student count

    # ✅ Ensure total pages is correctly calculated
    total_pages = max((total_students // per_page) + (1 if total_students % per_page > 0 else 0), 1)

    students = student.get_students(page, per_page)  # ✅ Fetch paginated students

    return render_template('student.html', students=students, page=page, total_pages=total_pages)


@student_bp.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page  # Calculate the correct offset

    total_pages, students = student.fetch_student(per_page, offset)  # Fetch paginated data

    return render_template('student.html', page=page, total_pages=total_pages, students=students)

@student_bp.route('/addstudent', methods=['GET', 'POST'])
def add_student():
    if request.method == 'GET':
        return render_template('add_student.html', courses=student.get_courses())  # ✅ Call model function

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
        return redirect(url_for('student_bp.add_student'))

    # Handle profile photo
    photo_url = profile_photo.filename if profile_photo else None  
    photo_public_id = "some_unique_id"

    try:
        student.add_student(stud_id, fname, lname, course, yearlevel, gender, photo_url, photo_public_id)  # ✅ Only call the model
        flash("Student added successfully!", "success")
    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred while adding the student. Try again.", "error")

    return redirect(url_for('students.home'))


@student_bp.route('/edit_student/<string:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if request.method == 'GET':  # Show the form
        student_data = student.get_student_by_id(student_id)  # ✅ Fetch current student data
        if not student_data:
            flash("Student not found!", "error")
            return redirect(url_for('students.home'))

        return render_template('edit_student.html', student=student_data)  # ✅ Display form

    # Handle form submission on POST request
    fname = request.form.get('fname', '')
    lname = request.form.get('lname', '')
    course = request.form.get('course', '')
    yearlevel = request.form.get('yearlevel', '')
    gender = request.form.get('gender', '')

    student.edit_student(student_id, fname, lname, course, yearlevel, gender)

    flash("Student updated successfully!", "success")

    # ✅ Fetch updated data to ensure changes are displayed
    updated_student_data = student.get_student_by_id(student_id)

    return render_template('student.html', student=updated_student_data, page=1, total_pages=1)
  # ✅ Reload form with new data



@student_bp.route('/student/delete_student//<string:student_id>',methods=['GET','POST'])
def delete_student(student_id):
    student.delete_student(student_id)
    return redirect(url_for('students.home'))
