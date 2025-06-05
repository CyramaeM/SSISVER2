import email
from flask import render_template, url_for, redirect, request, flash, Blueprint

auth_bp = Blueprint('auth',__name__)

ALLOWED_EXTENSIONS = {'png','jpg','jpeg'}

@auth_bp.route('/signup',methods=['GET','POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    
