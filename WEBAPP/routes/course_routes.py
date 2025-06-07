from flask import render_template, url_for, redirect, request, flash, Blueprint,session
import re
from webapp.models import course_models
from webapp.models.course_models import Course
from webapp.models.college_models import College


course_bp = Blueprint('course',__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


@course_bp.route('/coursehome', methods=['GET', 'POST'])
def course():
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('auth.login'))

    courses = Course.coursehome()  # ✅ Correct function call

    return render_template('course.html', courses=courses)


@course_bp.route('/addcourse', methods=['GET', 'POST'])
def add_course():
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        course_code = request.form.get('coursecode', '').strip()
        course_name = request.form.get('coursename', '').strip()
        college_belong = request.form.get('college', '').strip()

        success = Course.add_course(course_code, course_name, college_belong)  # ✅ Call the function

        if success:
            return redirect(url_for('course.course'))  # ✅ Redirect on success

    return render_template('add_course.html')



@course_bp.route('/edit_course/<string:coursecode>', methods=['GET', 'POST'])
def edit_course(coursecode):
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        course_name = request.form.get('coursename', '').strip()
        updated_course_code = request.form.get('coursecode', '').strip()  # ✅ Get coursecode from the form

        if not course_name or not updated_course_code:
            flash("All fields are required!", "danger")
            return redirect(url_for('course.edit_course', coursecode=coursecode))

        success = Course.edit_course(coursecode, course_name)  # ✅ Ensure correct function call

        if success:
            flash("Course updated successfully!", "success")
            return redirect(url_for('course.coursehome'))  # ✅ Redirect to home after update
        else:
            flash("Error updating course. Please try again.", "danger")

    course = Course.get_by_code(coursecode)  # ✅ Fetch course details

    if not course:
        flash("Course not found!", "danger")
        return redirect(url_for('course.coursehome'))  # ✅ Redirect instead of failing silently

    return render_template('edit_course.html', course=course)  # ✅ Pass course data to template


@course_bp.route('/deletecourse/<string:course_code>', methods=['POST'])
def delete_course(course_code):
    try:
        course.delete(course_code)
        flash("Course has been deleted successfully")
    except:
        flash("Course that has students enrolled cannot be deleted")
    
    return redirect(url_for('course.course'))