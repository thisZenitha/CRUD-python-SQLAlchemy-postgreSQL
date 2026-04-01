from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, set_access_cookies, jwt_required, get_jwt_identity, unset_jwt_cookies
from functools import wraps
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "TesZenitha"
                                                            #password:root
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:root@localhost/sampledb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["JWT_SECRET_KEY"] = "0987654321" 
jwt = JWTManager(app)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"] 
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
db=SQLAlchemy(app)
 
class Student(db.Model):
  __tablename__='students'
  id=db.Column(db.Integer,primary_key=True)
  fname=db.Column(db.String(40))
  lname=db.Column(db.String(40))
  phone=db.Column(db.String(40))
  password = db.Column(db.String(255), nullable=False)
  profile_pic = db.Column(db.String(255), nullable=True)
  status = db.Column(db.String(20), default='aktif')
  role = db.Column(db.String(20), default='user')

  def __init__(self,fname,lname,phone, password, profile_pic, status='aktif', role='user'):
    self.fname=fname
    self.lname=lname
    self.phone=phone
    self.password= password
    self.profile_pic=profile_pic
    self.status=status
    self.role=role

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = Student.query.get(user_id)

        if user and user.role == 'admin':
            return fn(*args, **kwargs)
        else:
            flash("Access Denied! Admin Only")
            return redirect(url_for('index'))
    return wrapper

@app.route('/')
@jwt_required(optional=True)
def index():
    user_id = get_jwt_identity()
    user_role = "guest"
    
    if user_id:
        user = Student.query.get(user_id)
        if user: 
            user_role = user.role
        else:
            user_role = "guest"
            
    all_students = Student.query.all()
    return render_template('index.html', list_users=all_students, role=user_role)

@app.route('/submit', methods=['POST']) 
def add_student(): 
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        raw_password = request.form['password']
        file = request.files.get('profile_pic')
        
        hashed_password = generate_password_hash(raw_password)
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = 'default.jpg' 

        new_student = Student(fname, lname, phone, hashed_password, filename)
        
        db.session.add(new_student)
        db.session.commit()
        
        flash("Registered Succesfully! Please Login")
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone')
    password = request.form.get('password')
    
    user = Student.query.filter_by(phone=phone).first()

    if user and check_password_hash(user.password, password):
        if user.status != 'aktif':
            flash("Account Non-active! Please Contact Our Administrator")
            return redirect(url_for('index'))

        access_token = create_access_token(identity=str(user.id))
        response = redirect(url_for('index'))
        set_access_cookies(response, access_token)
        flash(f"Welcome, {user.fname}!")
        return response
    else:
        flash("Wrong Phone Number or Password")
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    response = redirect(url_for('index'))
    unset_jwt_cookies(response)
    flash("Berhasil keluar!")
    return response
from flask_jwt_extended import unset_jwt_cookies

@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    response = redirect(url_for('index'))
    unset_jwt_cookies(response)
    flash("Session Run-out. Please Re-login!")
    return response

@jwt.unauthorized_loader
def my_unauthorized_callback(e):
    return redirect(url_for('index'))

def add_student():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        
        new_student = Student(fname, lname, phone)
        db.session.add(new_student)
        db.session.commit()
        
        flash("Student Added!")
        return redirect(url_for('index'))
 
    studentResult=db.session.query(Student).filter(Student.id==1)
    for result in studentResult:
        print(result.fname)
    
    return render_template('index.html', data=studentResult)

@app.route('/delete/<int:id>') 
@admin_required
def delete_student(id):
    student_to_delete = Student.query.get_or_404(id)
    try:
        db.session.delete(student_to_delete)
        db.session.commit()
        flash("Data Deleted Successfully")
        return redirect(url_for('index'))
    except:
        return "Problem with Deleting Data"

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_student(id):
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        student.fname = request.form.get('fname')
        student.lname = request.form.get('lname')
        student.phone = request.form.get('phone')
        
        try:
            db.session.commit()
            flash(f"Data {student.fname} berhasil diubah!")
            return redirect(url_for('index'))
        except:
            return "Terjadi masalah saat menyimpan data."
        
    return render_template('edit.html', data=student)

@app.route('/update/<int:id>', methods=['POST'])
def update_student(id):
    if request.method == 'POST':
        student = Student.query.get_or_404(id)

        student.fname = request.form['fname']
        student.lname = request.form['lname']
        student.phone = request.form['phone']
        
        try:
            db.session.commit()
            flash("Data Updated Succesfully!")
            return redirect(url_for('index'))
        except:
            return "Problem with Updating Data"
        
@app.route('/toggle_status/<int:id>')
@admin_required
def toggle_status(id):
    student = Student.query.get_or_404(id)
    
    if student.status == 'aktif':
        student.status = 'non-aktif'
    else:
        student.status = 'aktif'
    
    try:
        db.session.commit()
        flash(f"Status {student.fname} now {student.status}")
    except:
        db.session.rollback()
        flash("Failed status change")
        
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)