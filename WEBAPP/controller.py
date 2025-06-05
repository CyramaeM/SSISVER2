from flask import Blueprint,render_template,request,session,redirect,url_for,flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models.student_models import ALLOWED_EXTENSIONS,create_user,verify_user
from .. import mysql,csrf
import cloudinary
import cloudinary.uploader

controller = Blueprint('controller',__name__)


class error (Exception):
    pass
class InvalidID(Error):
    pass
class IDExists(Error):
    pass

@controller.route('')
@csrf.exempt
def base():
    return render_template('base.html')
@controller.route('/signup',methods=['GET','POST'])
@csrf.exempt
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Please fill in all fields", "danger")
            return redirect(url_for("auth.signup"))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        create_user(email, hashed_password)

        flash("Sign Up Successful!", "success")
        return redirect(url_for("auth.login"))

    return render_template('signup.html')

@controller.route('/login',methods=["GET","POST"])
@csrf.exempt
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user_id = verify_user(email, password)
        if user_id:
            session["user_id"] = user_id
            flash("Login successful!", "success")
            return redirect(url_for("student.home"))

        flash("Invalid email or password", "danger")

    return render_template("login.html")

@controller.route('/logout')
@csrf.exempt
def logout():
    session.pop('user_id', None) 
    flash("You have been logged out.", "info")
    return redirect(url_for('controller.login')) 
