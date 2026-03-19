from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
 
app = Flask(__name__)
app.secret_key = "TesZenitha"
                                                            #password:root
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:root@localhost/sampledb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)
 
class Student(db.Model):
  __tablename__='students'
  id=db.Column(db.Integer,primary_key=True)
  fname=db.Column(db.String(40))
  lname=db.Column(db.String(40))
  phone=db.Column(db.String(40))
 
  def __init__(self,fname,lname,phone):
    self.fname=fname
    self.lname=lname
    self.phone=phone

@app.route('/')
def index():
    all_students = Student.query.all()
    return render_template('index.html', list_users=all_students)

@app.route('/submit', methods=['POST']) # Tambahkan baris ini!
def add_student(): 
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        
        new_student = Student(fname, lname, phone)
        db.session.add(new_student)
        db.session.commit()
        
        flash("Student Berhasil Ditambahkan!")
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))
 
def add_student():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        
        new_student = Student(fname, lname, phone)
        db.session.add(new_student)
        db.session.commit()
        
        flash("Student Berhasil Ditambahkan!")
        return redirect(url_for('index'))
 
    studentResult=db.session.query(Student).filter(Student.id==1)
    for result in studentResult:
        print(result.fname)
    
    return render_template('index.html', data=studentResult)

@app.route('/delete/<int:id>') 
def delete_student(id):
    student_to_delete = Student.query.get_or_404(id)
    try:
        db.session.delete(student_to_delete)
        db.session.commit()
        flash("Data Berhasil Dihapus!")
        return redirect(url_for('index'))
    except:
        return "Terjadi masalah saat menghapus data."

@app.route('/edit/<int:id>')
def edit_student(id):
    student = Student.query.get_or_404(id)
    return render_template('edit.html', student=student)


@app.route('/update/<int:id>', methods=['POST'])
def update_student(id):
    if request.method == 'POST':
        student = Student.query.get_or_404(id)
        
        student.fname = request.form['fname']
        student.lname = request.form['lname']
        student.phone = request.form['phone']
        
        try:
            db.session.commit()
            flash("Data Berhasil Diperbarui!")
            return redirect(url_for('index'))
        except:
            return "Terjadi masalah saat memperbarui data."
if __name__ == "__main__":
    app.run(debug=True)