
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import check_password_hash
from sqlalchemy.orm import joinedload, relationship, backref
#from datetime import datetime
#from flask_migrate import Migrate


app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="JTgradebook",
    password="scep!chum7ZOMP.kref",
    hostname="JTgradebook.mysql.pythonanywhere-services.com",
    databasename="JTgradebook$comments",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
#migrate = Migrate(app, db)

app.secret_key = "something only you know"
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_id(self):
        return self.username

#
class Students(db.Model):

    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(200), nullable=False)
    lname = db.Column(db.String(200), nullable=False)
    major = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)

    def __init__(self, fname, lname, major,email):
        self.fname = fname
        self.lname = lname
        self.major = major
        self.email = email

    def __repr__(self):
        return '<Students %>' % self.fname


class Assignments(db.Model):

    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    assignment_name = db.Column(db.String(200), nullable=False)
    assignment_desc = db.Column(db.String(200), nullable=False)

    def __init__(self, assignment_name, assignment_desc):
        self.assignment_name = assignment_name
        self.assignment_desc = assignment_desc


    def __repr__(self):
        return '<Assignments %>' % self.assignment_name

class Grades(db.Model):

    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)
    assignment_id =db.Column(db.Integer, db.ForeignKey("assignments.id", ondelete="CASCADE"))
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"))
    percentage = db.Column(db.Float)

    students = relationship(Students, backref=backref("grades", cascade="all"))
    assignments = relationship(Assignments, backref=backref("grades", cascade="all"))

    def __init__(self, assignment_id, student_id, percentage):
        self.assignment_id = assignment_id
        self.student_id = student_id
        self.percentage = percentage

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

#class Comment(db.Model):
#
#   __tablename__ = "comments"
#
#    id = db.Column(db.Integer, primary_key=True)
#    content = db.Column(db.String(4096))
#    posted = db.Column(db.DateTime, default=datetime.now)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("main_page.html")
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

#    comment = Comment(content=request.form["contents"])
#    db.session.add(comment)
#    db.session.commit()
#    return redirect(url_for('index'))

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    user = load_user(request.form["username"])
    if user is None:
        return render_template("login_page.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for('index'))


@app.route("/students", methods=["GET", "POST"])
@login_required
def allstudents():
    if request.method == "GET":
        query = db.session.query(Students).order_by(Students.id.asc())
        return render_template("students.html", students=query)

@app.route("/add/students", methods=["GET", "POST"])
def add_students():
     if request.method == "GET":
        return render_template("add_user.html")
     if request.method == "POST":
        student = Students(request.form["fname"],request.form["lname"],request.form["major"],request.form['email'])
        db.session.add(student)
        db.session.commit()
        flash('New Student record was successfully added')
        # redirect(url_for('allstudents'))
     return render_template('add_user.html')


@app.route("/assignments")
def assignments():
    myAssignments = Assignments.query.all()
    return render_template("assignments.html", myAssignments=myAssignments)

@app.route("/add/assignment", methods=["GET", "POST"])
def add_assignment():
    if request.method == "GET":
        return render_template("add_assignment.html")
    if request.method == "POST":
        assignment = Assignments(request.form["assignment_name"],request.form["assignment_desc"])
        db.session.add(assignment)
        db.session.commit()
        flash('New assignment record was successfully added')
        # redirect(url_for('allstudents'))
    return render_template('add_assignment.html')

#Update Assignment ID working but name is not
@app.route("/update/<id>", methods=["GET", "POST"])
def assignmentedit(id):
    assignment_to_edit = Assignments.query.get_or_404(id)
    if request.method == "POST":
        assignment_to_edit.assignment_name = request.form['assignment_name']
        assignment_to_edit.assignment_desc = request.form['assignment_desc']

        try:
            db.session.commit()
            return redirect('/assignments')
        except:
            return "There was a problem"
    else:
        return render_template("edit_assignment.html", assignment_to_edit=assignment_to_edit)

@app.route("/sort", methods=["GET"])
@login_required
def sort():
    if request.method == "GET":
        query = db.session.query(Students).order_by(Students.lname.asc())
        return render_template("sort.html", students=query)


#Update student ID working but name is not
@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    student_to_edit = Students.query.get_or_404(id)
    if request.method == "POST":
        student_to_edit.fname = request.form['fname']
        student_to_edit.lname = request.form['lname']
        student_to_edit.major = request.form['major']
        student_to_edit.email = request.form['email']

        try:
            db.session.commit()
            return redirect('/students')
        except:
            return "There was a problem"
    else:
       return render_template("edit_user.html", student_to_edit=student_to_edit)


@app.route("/delete/<int:id>")
def delete(id):
    student_to_delete = Students.query.get_or_404(id)
    try:
        db.session.delete(student_to_delete)
        db.session.commit()
        return redirect('/students')
    except:
        return "there was a problem"

@app.route("/deleteAssignment/<int:id>")
def deleteassignment(id):
    assignments_to_delete = Assignments.query.get_or_404(id)
    try:
        db.session.delete(assignments_to_delete)
        db.session.commit()
        return redirect('/assignments')
    except:
        return "there was a problem"


@app.route("/grades", methods=["GET"])
@login_required
def grades():
    query = db.session.query(Grades).order_by(Grades.student_id.asc(),Grades.assignment_id.asc())
    query = query.options(
        joinedload(Grades.students),
        joinedload(Grades.assignments)
        )

    return render_template("grades.html", grades=query)

@app.route("/edit_grade/<int:id>", methods=["GET","POST"])
@login_required
def editgrades(id):
    grade_to_edit = Grades.query.get_or_404(id)

    if request.method == "POST":
        grade_to_edit.percentage = request.form['percentage']

        try:
            db.session.commit()
            return redirect('/grades')
        except:
            return "There was a problem"
    else:
       return render_template("edit_grades.html", grade_to_edit=grade_to_edit)

@app.route("/add_grade", methods=["GET","POST"])
@login_required
def addgrade():
    if request.method == "POST":
        grade_to_add = Grades(request.form['assignment_id'], request.form['student_id'], request.form['percentage'])
        db.session.add(grade_to_add)
        db.session.commit()
        flash('New grade record was successfully added')

        try:
            db.session.commit()
            return redirect('/grades')
        except:
            return "There was a problem"
    else:
       assignments = db.session.query(Assignments).order_by(Assignments.id.asc())
       students = db.session.query(Students).order_by(Students.id.asc())
       return render_template("add_grades.html", assignments=assignments, students=students)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))