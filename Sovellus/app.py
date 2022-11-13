from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///stenbras"
db = SQLAlchemy(app)

@app.route("/")
def index():
    result = db.session.execute("SELECT username FROM users")
    usernames = result.fetchall()
    return render_template("index.html", count=len(usernames), usernames=usernames) 

@app.route("/newuser")
def new():
    return render_template("newuser.html")

@app.route("/send", methods=["POST"])
def send():
    uname = request.form["uname"]
    upass= request.form["upass"]
    sql = "INSERT INTO messages (username,password) VALUES (:uname,:upass)"
    db.session.execute(sql, {"uname":uname,"upass":upass})
    db.session.commit()
    return redirect("/")

