import email
from flask import render_template, url_for, redirect, request, flash, Blueprint,session
from werkzeug.security import generate_password_hash,check_password_hash

from webapp.models.auth_models import auth


auth_bp = Blueprint('auth',__name__)

ALLOWED_EXTENSIONS = {'png','jpg','jpeg'}

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # ✅ Ensure required fields
        if not email or not password:
            flash("All fields are required!", "danger")
            return render_template('signup.html')

        success = auth.signup(email, password)
        if success:
            flash("Sign Up Successful!", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("An error occurred. Please try again.", "danger")
    
    return render_template('signup.html')


@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # ✅ Call model function instead of writing SQL here
        user = auth.get_user_by_email(email)

        if not user or not check_password_hash(user['password'], password):
            flash("Invalid email or password", "danger")
            return redirect(url_for('auth.login'))

        # ✅ Store user_id in session properly
        session['user_id'] = user['id']
        flash("Login successful!", "success")

        return redirect(url_for('students.home'))
    
    return render_template('login.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)  # ✅ Correctly removes user_id
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))  # ✅ Redirects properly after logout
