from flask import render_template, url_for, redirect, request, flash, Blueprint
from flask_login import login_required
import MySQLdb
import cloudinary
import re
from webapp.controller import login
from webapp.models.student_models import student

student_bp = Blueprint('students', __name__, template_folder='templates')


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@student_bp.route('/student/home')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page  # Calculate the correct offset

    total_pages, students = student.fetch_student(per_page, offset)  # Fetch paginated data

    return render_template('student.html', page=page, total_pages=total_pages, students=students)

@login_required
@student_bp.route('/student/addstudent', methods=['GET','POST'])
def add_student():
    print("Request Method:", request.method)  # Debugging request type
    print("Received Form Data:", request.form)  # Check what Flask actually gets

    if request.method != 'POST':
        print("Error: Form not submitted via POST")
        flash("Please submit the form correctly.", "error")
        return redirect(url_for('students.home'))


    stud_id = request.form.get('stud_id', '').strip()
    print("Received Student ID:", stud_id)  # Debugging


    if not stud_id:  # Check if empty
        print("Error: No Student ID received")  # Debugging step
        flash("Student ID is required!", "error")
        return redirect(url_for('students.home'))

    # Proceed with other fields
    fname = request.form.get('fname', '').strip()
    lname = request.form.get('lname', '').strip()
    course = request.form.get('course', '').strip()
    yearlevel = request.form.get('yearlevel', '').strip()
    gender = request.form.get('gender', '').strip()
    profile_photo = request.files.get('profile_photo')

    try:
        student.add_student(stud_id, fname, lname, course, yearlevel, gender, profile_photo)
        flash("Data Inserted Successfully", "success")
    except Exception as e:
        print("Database Error:", e)  # Debugging database issues
        flash("Student ID already exists. Please try another.", 'error')

    return redirect(url_for('students.home'))

@student_bp.route('/student/edit_student/<string:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):  # Add student_id as parameter
    student_id = request.form.get('student_id', '').strip()
    fname = request.form.get('fname', '')
    lname = request.form.get('lname', '')
    course = request.form.get('course', '')
    yearlevel = request.form.get('yearlevel', '')
    gender = request.form.get('gender', '')

    student.edit_student(student_id, fname, lname, course, yearlevel, gender)
    return redirect(url_for('students.home'))



@student_bp.route('/student/delete_student//<string:student_id>',methods=['GET','POST'])
def delete_student(student_id):
    student.delete_student(student_id)
    return redirect(url_for('students.home'))
