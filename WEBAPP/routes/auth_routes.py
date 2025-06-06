import email
from flask import render_template, url_for, redirect, request, flash, Blueprint,session
from werkzeug.security import generate_password_hash,check_password_hash


auth_bp = Blueprint('auth',__name__)

ALLOWED_EXTENSIONS = {'png','jpg','jpeg'}

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # Process form data
            username = request.form['username']
            password = request.form['password']
            
            # Validate and create user
            if not username or not password:
                return render_template('signup.html', error="All fields are required")
            
            # Add user creation logic here
            new_user = create_user(username, password)
            
            # Must return after successful creation
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            # Must return in error case too
            return render_template('signup.html', error=str(e))
    
    # Must return for GET requests
    return render_template('signup.html')
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Received login request")  # Debugging step

        email = request.form.get('email')
        password = request.form.get('password')

        print("Email entered:", email)
        print("Password entered:", password)

        # Check if session data already exists
        stored_email = session.get('user_email')
        stored_password_hash = session.get('user_password_hash')

        print("Stored email before login:", stored_email)
        print("Stored password hash before login:", stored_password_hash)

        # If stored values exist, validate login
        if stored_email and stored_password_hash and email == stored_email and check_password_hash(stored_password_hash, password):
            session['logged_in'] = True  # Mark user as logged in
            flash("Login successful!", "success")
            return redirect(url_for('students.home'))  # Redirect to home page
        
        # If no stored data exists, register this email/password in session
        if not stored_email and not stored_password_hash:
            session['user_email'] = email
            session['user_password_hash'] = generate_password_hash(password)  # Store hashed password
            session['logged_in'] = True  # Mark as logged in

            print("Session after storing user:", session)  # Debugging step
            flash("Account created & logged in!", "success")
            return redirect(url_for('students.home'))  # Redirect after setting session values
        
        flash("Invalid credentials", "error")
        print("Login failed: Invalid credentials")  # Debugging step

    return render_template('login.html')