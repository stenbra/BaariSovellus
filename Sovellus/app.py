from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, render_template, request, session
import os
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///stenbras"
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)

weekdayList = ["Ma","Ti","Ke","To","Pe","La","Su"]


@app.route("/", methods=["GET", "POST"])
def index():
    result = db.session.execute("SELECT * FROM bars")
    bars = result.fetchall()
    return render_template("index.html", count=len(bars), bars=bars)

@app.route("/removebar", methods=["GET", "POST"])
def removebar():
    if request.method == "POST":
        bar_id = request.form["bar_id"]
        remove_bar(bar_id)
        return redirect("/")

@app.route("/bar", methods=["GET", "POST"])
def barpage():
    if request.method == "POST":
        bar_id = request.form["bar_id"]
        if not bar_id:
            return redirect("/")
        if "r_id" in request.form:
            bar_id = request.form["bar_id"]
            r_id = request.form["r_id"]
            if not remove_review(r_id):
                redirect("/")
            if not bar_id:
                redirect("/")
        if user_id() and "rating" in request.form:
            if not check_if_already_reviewed(user_id(),bar_id):
                rating = request.form["rating"]
                comment = request.form["comment"]
                if not add_review(user_id(),bar_id,rating,comment):
                    return redirect("/")
        data = get_bar_data(bar_id)
        return render_template("bar.html",name=data["name"],description=data["description"],address=data["address"],hours=data["hours"],reviews=data["reviews"],weekLabels= weekdayList)

@app.route("/editbar", methods=["GET","POST"])
def editbar():
    if request.method =="GET":
        return render_template("editbar.html")
    if request.method == "POST":
        barname = request.form["barname"]
        description = request.form["description"]
        address = request.form["address"]
        open = []
        close = []
        for i in range(1,8):
            open.append(request.form[str(i)+"o"])
            close.append(request.form[str(i)+"c"])
        if edit_bar(barname,description,address,open,close):
            return redirect("/")
        return render_template("editbar.html",message="jotain meni pieleen")


#################################### USER STUFF
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["uname"]
        password1 = request.form["upass"]
        password2 = request.form["upass2"]
        check = request.form.get("barowner")
        if check:
            barowner = True
        else:
            barowner=False
        if password1 != password2:
            return render_template("register.html", message="Salasanat eroavat")
        if register_user(username, password1,barowner):
            return redirect("/")
        else:
            return render_template("register.html", message="Rekisteröinti ei onnistunut")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["uname"]
        password = request.form["upass"]
        if login_user(username, password):
            return redirect("/")
        else:
            return render_template("login.html", message="Väärä tunnus tai salasana")

@app.route("/logout")
def logout():
    delete_sessions()
    return redirect("/")


##### user stuff
def delete_sessions():
    del session["user_id"]
    del session["username"]
    del session["admin"]
    del session["barowner"]

def login_user(username, password):
    try:
        sql = "SELECT id, password,admin,barowner FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()
    except:
        return False
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = username
            session["admin"] = user.admin
            session["barowner"]= user.barowner
            return True
        else:
            return False

def register_user(username, password,barowner):
    hash_pass = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password,admin,barowner) VALUES (:username,:password,:admin,:barowner)"
        db.session.execute(sql, {"username":username, "password":hash_pass, "admin":False,"barowner":barowner})
        db.session.commit()
    except:
        return False
    return login_user(username, password)

def user_id():
    return session.get("user_id")

##### bar stuff
def edit_bar(barname,description,address,opening,closing):
    if not user_id():
        return False
    try:
        sql = "SELECT id FROM bars WHERE name=:barname"
        result = db.session.execute(sql, {"barname":barname})
        bar = result.fetchone()
    except:
        pass
    if not bar:
        return add_bar(barname,description,address,opening,closing)
    else:
        return update_bar()

def add_bar(barname,description,address,opening,closing):
    try:
        sql = "INSERT INTO bars (name,owner_id) VALUES (:name,:owner_id)"
        db.session.execute(sql, {"name":barname,"owner_id":user_id()})
        db.session.commit()
    except:
        return False
    try:
        sql = "SELECT id FROM bars WHERE name=:barname"
        result = db.session.execute(sql, {"barname":barname})
        bar = result.fetchone()
    except:
        return False
    if not bar:
        return False
    try:
        sql = "INSERT INTO description (description,bar_id) VALUES (:description,:bar_id)"
        db.session.execute(sql, {"description":description,"bar_id":bar.id})
        db.session.commit()
    except:
        return False
    try:
        sql = "INSERT INTO location (address,bar_id) VALUES (:address,:bar_id)"
        db.session.execute(sql, {"address":address,"bar_id":bar.id})
        db.session.commit()
    except:
        return False
    for i in range(7):
        if opening[i] or closing[i]:
            try:
                sql = "INSERT INTO openhours (weekday,opening,closing,bar_id) VALUES (:weekday,:opening,:closing,:bar_id)"
                db.session.execute(sql,{"weekday":i+1,"opening":opening[i],"closing":closing[i],"bar_id":bar.id})
                db.session.commit()
            except:
                pass
    return True

def update_bar():
    pass

def get_bar_data(bar_id):
    datadict ={}
    sql = "SELECT id,name FROM bars WHERE id=:id"
    result = db.session.execute(sql, {"id":bar_id})
    datadict["name"] = result.fetchone()
    sql = "SELECT description FROM description WHERE bar_id=:id"
    result = db.session.execute(sql, {"id":bar_id})
    datadict["description"] = result.fetchone()
    sql = "SELECT address FROM location WHERE bar_id=:id"
    result = db.session.execute(sql, {"id":bar_id})
    datadict["address"] = result.fetchone()
    sql = "SELECT weekday,opening,closing FROM openhours WHERE bar_id=:id"
    result = db.session.execute(sql, {"id":bar_id})
    datadict["hours"] = result.fetchall()
    sql = "SELECT T.id,T.rating,T.comment,U.username FROM reviews T,users U WHERE T.bar_id=:b_id AND U.id=T.user_id"
    result = db.session.execute(sql, {"b_id":bar_id})
    datadict["reviews"] = result.fetchall()
    return datadict
def add_review(user_id,bar_id,rating,comment):
    try:
        sql = "INSERT INTO reviews (comment,rating,user_id,bar_id) VALUES (:comment,:rating,:user_id,:bar_id)"
        db.session.execute(sql,{"comment":comment,"rating":rating,"user_id":user_id,"bar_id":bar_id})
        db.session.commit()
        return True
    except:
        return False
def remove_review(id):
    try:
        sql = "DELETE FROM reviews WHERE id=:r_id"
        db.session.execute(sql,{"r_id":id})
        db.session.commit()
    except:
        return False
def check_if_already_reviewed(u_id,bar_id):
    try:
        sql = "SELECT rating FROM reviews WHERE bar_id=:b_id AND user_id=:u_id"
        result = db.session.execute(sql, {"b_id":bar_id,"u_id":u_id})
        a = result.fetchone()
    except:
        return False
    if not a:
        return False
    return True
def remove_bar(id):
    try:
        sql = "DELETE FROM bars WHERE id=:bar_id"
        db.session.execute(sql,{"bar_id":id})
        db.session.commit()
    except:
        return False
