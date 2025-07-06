from flask import render_template, url_for, redirect, request, flash, Blueprint,session
from flask_wtf.csrf import generate_csrf

import re
from webapp.models import course_models
from webapp.models.course_models import Course
from webapp.models.college_models import College


course_bp = Blueprint('course',__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


@course_bp.route('/coursehome', methods=['GET', 'POST'])
def course():

    courses = Course.coursehome()  # ✅ Correct function call

    return render_template('course.html', courses=courses)


@course_bp.route('/addcourse', methods=['GET', 'POST'])
def add_course():
    colleges = College.get_all_colleges()  # ✅ Correct function name

    if request.method == 'POST':
        course_code = request.form.get('coursecode', '').strip()
        course_name = request.form.get('coursename', '').strip()
        college_belong = request.form.get('college', '').strip()

        success = Course.add_course(course_code, course_name, college_belong)

        if success:
            return redirect(url_for('course.course'))  

    return render_template('add_course.html', colleges=colleges)  # ✅ Pass colleges to template

@course_bp.route('/edit_course/<string:coursecode>', methods=['GET', 'POST'])
def edit_course(coursecode):
    colleges = College.get_all_colleges()  # Fetch colleges for dropdown
    
    if request.method == 'POST':
        course_name = request.form.get('course_name', '').strip()
        college_belong = request.form.get('college', '').strip() or None  # Handle empty selection
        
        # Update both course name and college
        success = Course.edit_course(coursecode, course_name, college_belong)
        
        if success:
            flash("Course updated successfully!", "success")
            return redirect(url_for('course.course'))
        else:
            flash("Error updating course. Please try again.", "danger")

    # Fetch the current course data
    course = Course.get_by_code(coursecode)
    
    if not course:
        flash("Course not found!", "danger")
        return redirect(url_for('course.course'))

    return render_template(
        'edit_course.html', 
        course=course, 
        colleges=colleges,
        csrf_token=generate_csrf()
    )


@course_bp.route('/deletecourse/<string:course_code>', methods=['POST'])
def delete_course(course_code):
    try:
        result = Course.delete_course(course_code)

        if result:
            # The delete method already flashes the appropriate message
            pass
        else:
            flash("Course deletion failed. Please try again.", "danger")

    except Exception as e:
        print("Route Error:", e)  # Optional: log the error
        flash("An unexpected error occurred while deleting the course.", "danger")

    return redirect(url_for('course.course'))
