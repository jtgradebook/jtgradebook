
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import check_password_hash
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


@app.route("/sort", methods=["GET"])
@login_required
def sort():
    if request.method == "GET":
        query = db.session.query(Students).order_by(Students.lname.asc())
        return render_template("sort.html", students=query)




@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))