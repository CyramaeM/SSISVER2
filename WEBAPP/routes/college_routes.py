from flask import render_template, url_for, redirect, request, flash, Blueprint,session
import re
from webapp.models.college_models import college


college_bp = Blueprint('college',__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@college_bp.route('/college/collegehome',methods=['GET','POST'])
def college():
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('controller.login'))
    return render_template('college.html')

@college_bp.route('/college/addcollege',methods=['GET','POST'])
def add_college():
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('controller.login'))
    if request.method == 'POST':
        collegecode = request.form['collegecode']
        collegename = request.form['collegename']
    try:
        college.add_college(collegecode, collegename)
        flash("Data Inserted Successfully")
    except:
        flash("College code already exists. Please try another.")
    
    return render_template('add_college.html')

@college_bp.route('/college/editcollege',methods=['GET','POST'])
def edit_college():
    if request.method == 'POST':
            # Get form data for college
        college_code = request.form.get('college_code')
        college_name = request.form.get('college_name')
        college.edit_college(college_code,college_name)
        flash("Data updated successfully")
        return render_template('edit_college.html')
    else:
        if not college:
                flash("College not found!", "danger")
                return redirect(url_for('controller.collegehome')) 

        return render_template('edit_college.html')
    

@college_bp.route('/college/deletecollege',methods=['GET','POST'])
def delete_college(college_code):
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('controller.login'))
    try:
        college.delete_college(college_code)
        flash("College has been deleted successfully")
        return redirect(url_for('controller.collegehome'))
    except:
        flash("College that has existing courses cannot be deleted")
        return redirect(url_for('controller.collegehome'))