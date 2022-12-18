from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, render_template, request, session
from os import getenv
import os
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///stenbras"#getenv("DATABASE_URL")
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)#getenv("SECRET_KEY")

weekdayList = ["Ma","Ti","Ke","To","Pe","La","Su"]


@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("last_bar"):
        del session["last_bar"]
    if request.method == "GET":
        bars = get_bars()
        return render_template("index.html", count=len(bars), bars=bars)
    if request.method == "POST":
        if "owner_id" in request.form:
            bars = get_bars_filter_by_owner(request.form["owner_id"])
        elif "search" in request.form:
            bars = get_bars_filter_by_word(request.form["search"])
        elif "top" in request.form:
            bars = get_bars_filter_by_rating()
        return render_template("index.html", count=len(bars), bars=bars)

@app.route("/removebar", methods=["GET", "POST"])
def removebar():
    if request.method == "POST":
        bar_id = request.form["bar_id"]
        remove_bar(bar_id)
        return redirect("/")

@app.route("/bar", methods=["GET", "POST"])
def barpage():
    if request.method == "GET":
        if not session.get("last_bar"):
            redirect("/")
        bar_id=session["last_bar"]
        data = get_bar_data(bar_id)
        review_data = get_bar_reviews(bar_id)
        return render_template("bar.html",bardata=data,reviews=review_data,weekLabels= weekdayList)

    if request.method == "POST":
        bar_id = request.form["bar_id"]
        if not bar_id and session.get("last_bar"):
            bar_id = session["last_bar"]
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
        review_data = get_bar_reviews(bar_id)
        session["last_bar"]= bar_id
        return render_template("bar.html",bardata=data,reviews=review_data,weekLabels= weekdayList)

@app.route("/editbar", methods=["GET","POST"])
def editbar():
    if request.method =="GET":
        return render_template("editbar.html")
    if request.method == "POST":
        if "bar_id" in request.form:
            data = get_bar_data(request.form["bar_id"])
            presentDays =[]
            for i in data:
                if i.weekday:
                    presentDays.append(i.weekday-1)
            return render_template("editbar.html",bardata=data,weekLabels= weekdayList,presentDays=presentDays)
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
            if session.get("last_bar"):
                return redirect("/bar")
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
            if session.get("last_bar"):
                return redirect("/bar")
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
    user = get_user(username)
    print(user)
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

def get_user(username):
    try:
        sql = "SELECT id, password,admin,barowner FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username})
        return result.fetchone()
    except:
        return None


def register_user(username, password,barowner):
    add_user(username, password,barowner)
    return login_user(username, password)

def add_user(username, password,barowner):
    hash_pass = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password,admin,barowner) VALUES (:username,:password,:admin,:barowner)"
        db.session.execute(sql, {"username":username, "password":hash_pass, "admin":False,"barowner":barowner})
        db.session.commit()
    except:
        return False
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
        return update_bar(barname,description,address,opening,closing)

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

def update_bar(barname,description,address,opening,closing):
    try:
        sql = "SELECT id FROM bars WHERE name=:barname"
        result = db.session.execute(sql, {"barname":barname})
        bar = result.fetchone()
    except:
        return False
    if not bar:
        return False
    try:
        sql = "UPDATE description SET description=:description WHERE description.bar_id=:bar_id"
        db.session.execute(sql, {"description":description,"bar_id":bar.id})
        db.session.commit()
    except:
        return False
    try:
        sql = "UPDATE location SET address=:address WHERE location.bar_id=:bar_id"
        db.session.execute(sql, {"address":address,"bar_id":bar.id})
        db.session.commit()
    except:
        return False
    for i in range(7):
        sql = "SELECT id FROM openhours WHERE weekday=:weekday AND bar_id=:bar_id"
        result =db.session.execute(sql, {"weekday":i+1,"bar_id":bar.id})
        openHours=result.fetchone()
        if not openHours:
            if opening[i] or closing[i]:
                try:
                    sql = "INSERT INTO openhours (weekday,opening,closing,bar_id) VALUES (:weekday,:opening,:closing,:bar_id)"
                    db.session.execute(sql,{"weekday":i+1,"opening":opening[i],"closing":closing[i],"bar_id":bar.id})
                    db.session.commit()
                except:
                    pass
        else:
            if not opening[i] and not closing[i]:
                sql = "DELETE FROM openhours WHERE bar_id=:bar_id AND weekday=:weekday"
                db.session.execute(sql,{"bar_id":bar.id,"weekday":i+1})
                db.session.commit()
            else:
                sql = "UPDATE openhours SET opening=:opening,closing=:closing WHERE weekday=:weekday AND bar_id=:bar_id"
                db.session.execute(sql, {"opening":opening[i],"closing":closing[i],"weekday":i+1,"bar_id":bar.id})
                db.session.commit()
    return True

def get_bar_data(bar_id):
    sql = "SELECT DISTINCT bars.id,bars.owner_id,bars.name,description.description,location.address,openhours.weekday,openhours.opening,openhours.closing,ROUND(AVG(reviews.rating),1) AS rating FROM bars LEFT JOIN description ON bars.id = description.bar_id LEFT JOIN location ON bars.id=location.bar_id LEFT JOIN openhours ON bars.id = openhours.bar_id LEFT JOIN  reviews ON reviews.bar_id = bars.id WHERE bars.id =:id GROUP BY bars.id,description.id,location.id,openhours.id ORDER BY rating"
    result = db.session.execute(sql, {"id":bar_id})
    bardata = result.fetchall()
    return bardata

def get_bar_reviews(bar_id):
    sql = "SELECT T.id,T.rating,T.comment,U.username FROM reviews T,users U WHERE T.bar_id=:b_id AND U.id=T.user_id"
    result = db.session.execute(sql, {"b_id":bar_id})
    reviews = result.fetchall()
    return reviews
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
def get_bat_reviewScore(bar_id):
    try:
        sql = "SELECT AVG(rating) FROM reviews WHERE bar_id =:id"
        result = db.session.execute(sql, {"b_id":bar_id,"u_id":u_id})
        a = result.fetchone()
        return a
    except:
        pass
def remove_bar(id):
    try:
        sql ="DELETE FROM reviews WHERE bar_id=:bar_id"
        db.session.execute(sql,{"bar_id":id})
        db.session.commit()
        sql = "DELETE FROM bars WHERE id=:bar_id"
        db.session.execute(sql,{"bar_id":id})
        db.session.commit()
    except:
        return False
def get_bars():
    result = db.session.execute("SELECT bars.name, bars.id, bars.owner_id, ROUND(AVG(reviews.rating),1) AS rating FROM bars LEFT JOIN  reviews ON reviews.bar_id = bars.id GROUP BY bars.id")
    return result.fetchall()
def get_bars_filter_by_word(word):
    word= "%"+str(word)+"%"
    result = db.session.execute("SELECT bars.name, bars.id, bars.owner_id, ROUND(AVG(reviews.rating),1) AS rating FROM bars LEFT JOIN  reviews ON reviews.bar_id = bars.id LEFT JOIN description ON description.bar_id = bars.id WHERE bars.name LIKE :word OR description.description LIKE :word GROUP BY bars.id",{"word":word})
    return result.fetchall()
def get_bars_filter_by_owner(owner_id):
    result = db.session.execute("SELECT bars.name, bars.id, bars.owner_id, ROUND(AVG(reviews.rating),1) AS rating FROM bars LEFT JOIN  reviews ON reviews.bar_id = bars.id WHERE bars.owner_id=:owner_id GROUP BY bars.id",{"owner_id":owner_id})
    return result.fetchall()
def get_bars_filter_by_rating():
    result = db.session.execute("SELECT bars.name, bars.id, bars.owner_id, ROUND(AVG(reviews.rating),1) AS rating FROM bars LEFT JOIN  reviews ON reviews.bar_id = bars.id WHERE rating IS NOT NULL GROUP BY bars.id ORDER BY rating DESC")
    return result.fetchall()
