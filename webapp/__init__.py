from flask import Flask, render_template,request
from webapp.database import mysql
from config import DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, SECRET_KEY
from webapp.models.student_models import student
from flask_wtf.csrf import CSRFProtect
import cloudinary
import cloudinary.uploader
import cloudinary.api


csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, template_folder="templates", instance_relative_config=True)
    app.config.from_mapping (
        SECRET_KEY=SECRET_KEY,
        MYSQL_USER=DB_USERNAME,
        MYSQL_PASSWORD=DB_PASSWORD,
        MYSQL_DB=DB_NAME,
        MYSQL_HOST=DB_HOST,
        MYSQL_PORT=3306,
        MYSQL_CURSORCLASS='DictCursor'
    )

    cloudinary.config(
        cloud_name = 'dbth29nsw',
        api_key = '875432953529479',
        api_secret = 'Pd9SnwsUh40BXu67DaOh6LcxI4s'
        )
    mysql.init_app(app)

    with app.app_context():
        try:
            conn = mysql.connection
            cur = conn.cursor()
            cur.execute("SELECT DATABASE();")
            print("Connected to:", cur.fetchone())
        except Exception as e:
            print(f"❌ MySQL Error: {str(e)}")


    csrf.init_app(app)

    @app.route('/',methods=['GET','POST'])
    def index():
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page
        
        total_pages, students = student.fetch_student(per_page, offset)
        
        return render_template('student.html',  students=students, page=page, total_pages=total_pages)

    from.routes.auth_routes import auth_bp
    from .routes.college_routes import college_bp
    from .routes.course_routes import course_bp
    from .routes.student_routes import student_bp
    
    app.register_blueprint(auth_bp,url_prefix='/auth')
    app.register_blueprint(college_bp,url_prefix='/college')
    app.register_blueprint(course_bp,url_prefix='/course')
    app.register_blueprint(student_bp,url_prefix='/student')


    return app
