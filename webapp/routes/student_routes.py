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
    # Get sorting parameters from request
    sort_by = request.args.get('sort_by', 'id_number')
    sort_dir = request.args.get('sort_dir', 'ASC')
    course_details = student.get_course_details()
    
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '').strip()
    per_page = 10
    offset = (page - 1) * per_page

    if query:
        total_pages, students = student.search(
            query, 
            per_page=per_page, 
            offset=offset,
            sort_by=sort_by,
            sort_dir=sort_dir
        )
    else:
        total_pages, students = student.fetch_student(
            per_page, 
            offset,
            sort_by=sort_by,
            sort_dir=sort_dir
        )
    
    # Pass sorting parameters to template
    return render_template('student.html', 
                           page=page, 
                           total_pages=total_pages, 
                           students=students,
                           course_details=course_details,
                           query=query,
                           sort_by=sort_by,
                           sort_dir=sort_dir)  # Pass query to template
                           
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Then update the add_student route
@student_bp.route('/addstudent', methods=['GET', 'POST'])
def add_student():
    if request.method == 'GET':
        course_details = student.get_course_details()
        return render_template('add_student.html', course_details=course_details)
    
    # Retrieve form data
    stud_id = request.form.get('stud_id', '').strip()
    # Validate student ID format
    if not re.match(r'^\d{4}-\d{4}$', stud_id):
        flash('Student ID must be in format 0000-0000', 'error')
        return redirect(url_for('students.add_student'))
    
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
        # Strict file type validation
        if not allowed_file(profile_photo.filename):
            flash("Invalid file type. Only PNG and JPG/JPEG images are allowed.", "error")
            return redirect(url_for('students.add_student'))
        
        # Validate file size (5MB max)
        profile_photo.seek(0, 2)  # Seek to end of file
        file_size = profile_photo.tell()
        profile_photo.seek(0)  # Reset file pointer
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            flash("File size exceeds 5MB limit. Please upload a smaller image.", "error")
            return redirect(url_for('students.add_student'))
        
        try:
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                profile_photo,
                folder="student_profiles/",
                resource_type="image"
            )
            photo_url = upload_result['secure_url']
            photo_public_id = upload_result['public_id']
        except Exception as e:
            print("Cloudinary Upload Error:", e)
            flash("Error uploading profile photo. Please try again.", "error")
            return redirect(url_for('students.add_student'))
    
    try:
        student.add_student(stud_id, fname, lname, course, yearlevel, gender, photo_url, photo_public_id)
        flash("Student added successfully!", "success")
    except MySQLdb.IntegrityError as e:
        print("Database Integrity Error:", e)
        flash("A student with that ID number already exists!", "error")
    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred while adding the student. Try again.", "error")
    
    return redirect(url_for('students.home'))

# Update the edit_student route similarly
@student_bp.route('/edit_student/<string:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
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
            photo_url = None
            photo_public_id = None
            current_student = student.get_student_by_id(student_id)
            
            if profile_photo and profile_photo.filename != '':
                # Strict file type validation
                if not allowed_file(profile_photo.filename):
                    flash("Invalid file type. Only PNG and JPG/JPEG images are allowed.", "error")
                    return redirect(url_for('students.edit_student', student_id=student_id))
                
                # Validate file size (5MB max)
                profile_photo.seek(0, 2)  # Seek to end of file
                file_size = profile_photo.tell()
                profile_photo.seek(0)  # Reset file pointer
                
                if file_size > 5 * 1024 * 1024:  # 5MB
                    flash("File size exceeds 5MB limit. Please upload a smaller image.", "error")
                    return redirect(url_for('students.edit_student', student_id=student_id))
                
                # Upload new photo
                upload_result = cloudinary.uploader.upload(
                    profile_photo,
                    folder="student_profiles/",
                    resource_type="image"
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
                # Keep existing photo
                if current_student:
                    photo_url = current_student.get('profile')
                    photo_public_id = current_student.get('profile_id')

            # Update student
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


@student_bp.route('/search_student', methods=['GET'])
def search_student():
    query = request.args.get('query', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for('students.home'))

    total_pages, results = student.search(query, per_page=per_page, offset=offset)
    course_details = student.get_course_details()

    return render_template('student.html',
                           students=results,  # Pass as 'students' for consistent template handling
                           course_details=course_details,
                           query=query,
                           page=page,
                           total_pages=total_pages)