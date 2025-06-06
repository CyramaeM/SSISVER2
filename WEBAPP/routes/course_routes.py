from flask import render_template, url_for, redirect, request, flash, Blueprint
import re
from webapp.models.course_models import course


course_bp = Blueprint('course',__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


@course_bp.route('/coursehome',methods=['GET','POST'])
def course():
    courses = course.get_all()
    colleges = course.get_colleges()
    return render_template('course.html', course_list=courses, college=colleges)

@course_bp.route('/course/addcourse',methods=['GET',"POST"])
def add_course():
    course_code = request.form['coursecode']
    course_name = request.form['coursename']
    college_belong = request.form['college']
    try: 
        course.add_course(course_code,course_name,college_belong)
        flash("Course added successfully!", "success")
    except:
        flash("Course code already exists. Please try another.")
    return render_template('add_course.html',)

@course_bp.route('/course/edit_course',methods=['GET','POST'])
def edit_course():
    course_code = request.form.get('course_code')
    course_name = request.form.get('course_name')
    course.edit_course(course_code,course_name)
    return redirect(url_for('course.course'))

@course_bp.route('/course/deletecourse',methods=['GET','POST'])
def delete_course(course_code):
    try:
        course.delete(course_code)
        flash("Course has been deleted successfully")
    except:
        flash("Course that has students enrolled cannot be deleted")
    
    return redirect(url_for('course.course'))