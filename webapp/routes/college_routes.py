from flask import render_template, url_for, redirect, request, flash, Blueprint,session
import re
from webapp.models import college_models
from webapp.models.college_models import College


college_bp = Blueprint('college',__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@college_bp.route('/collegehome',methods=['GET','POST'])
def college():
    colleges = College.collegehome()

    return render_template('college.html', colleges=colleges)

@college_bp.route('/addcollege', methods=['GET', 'POST'])
def add_college():
    if request.method == 'POST':
        collegecode = request.form['collegecode']
        collegename = request.form['collegename']

        success = College.add_college(collegecode, collegename)  # ✅ Call the function

        if success:
            return redirect(url_for('college.college'))  # ✅ Redirect on success

    return render_template('add_college.html')  # ✅ Reload form if adding fails


@college_bp.route('/edit_college/<string:college_code>', methods=['GET', 'POST'])
def edit_college(college_code):

    if request.method == 'POST':
        college_name = request.form.get('college_name', '').strip()

        if not college_name:
            flash("College Name is required!", "danger")
            return redirect(url_for('college.edit_college', college_code=college_code))

        success = College.edit_college(college_code, college_name)  # ✅ Capture return value

        if success:
            return redirect(url_for('college.college'))  # ✅ Redirect after success
        else:
            return redirect(url_for('college.edit_college', college_code=college_code))  # ✅ Retry edit page

    college = College.get_by_code(college_code)

    if not college:
        flash("College not found!", "danger")
        return redirect(url_for('college.collegehome'))

    return render_template('edit_college.html', college=college)


    

@college_bp.route('/delete_college/<string:college_code>', methods=['POST'])
def delete_college(college_code):
    success = College.delete_college(college_code)  # ✅ Attempt deletion

    if success:
        flash("College deleted successfully!", "success")
    else:
        flash("Cannot delete college. Students are still enrolled in its courses.", "danger")

    return redirect(url_for('college.college'))
