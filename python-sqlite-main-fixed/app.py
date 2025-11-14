# tambahkan beberapa library session, wraps, generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# tambahkan app.secret_key
app.secret_key = '99dd0635533b320174ffffe82832b62cd956875d86dd6542981672641eee5aa7'

# Tambahkan CSRF
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = '99dd0635533b320174ffffe82832b62cd956875d86dd6542981672641eee5aa7'


# menambah database user
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

# Tambahkan sanitize text
import re
def sanitize_text(text):
    text = text.strip()
    # hilangkan < > agar tidak bisa membuat tag html
    text = text.replace("<", "").replace(">", "")
    # batasi panjang
    if len(text) > 100:
        text = text[:100]
    return text

# menambah fungsi kembali ke halaman login jika tidak terautentikasi
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# menambah fungsi register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            return redirect(url_for('register'))
        ph = generate_password_hash(password)
        user = User(username=username, password_hash=ph)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# menambah fungsi login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
    return render_template('login.html')

# menambah fungsi logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
# memanggil fungsi autentikasi
@login_required
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
# memanggil fungsi autentikasi
@login_required
def add_student():
    name = sanitize_text(request.form['name'])
    age = sanitize_text(request.form['age'])
    grade = sanitize_text(request.form['grade'])
    

    # connection = sqlite3.connect('instance/students.db')
    # cursor = connection.cursor()

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()

    # query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    # cursor.execute(query)
    # connection.commit()
    # connection.close()

    # meggunakan fungsi SQLAlchemy ORM
    student = Student(name=name, age=age, grade=grade)
    db.session.add(student)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<string:id>') 
# memanggil fungsi autentikasi
@login_required
def delete_student(id):
    # RAW Query
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
# memanggil fungsi autentikasi
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = sanitize_text(request.form['name'])
        student.age = sanitize_text(request.form['age'])
        student.grade = sanitize_text(request.form['grade'])
        
        # RAW Query
        # db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        # db.session.commit()

        # meggunakan fungsi SQLAlchemy ORM
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
