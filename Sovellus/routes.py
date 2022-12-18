from flask import redirect, render_template, request, session
import queries as query
from app import app
from werkzeug.security import check_password_hash, generate_password_hash

weekdayList = ["Ma","Ti","Ke","To","Pe","La","Su"]


@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("last_bar"):
        del session["last_bar"]
    if request.method == "GET":
        bars = query.get_bars()
        return render_template("index.html", count=len(bars), bars=bars)
    if request.method == "POST":
        if "owner_id" in request.form:
            bars = query.get_bars_filter_by_owner(request.form["owner_id"])
        elif "search" in request.form:
            bars = query.get_bars_filter_by_word(request.form["search"])
        elif "top" in request.form:
            bars = query.get_bars_filter_by_rating()
        return render_template("index.html", count=len(bars), bars=bars)

@app.route("/removebar", methods=["GET", "POST"])
def removebar():
    if request.method == "POST":
        bar_id = request.form["bar_id"]
        query.remove_bar(bar_id)
        return redirect("/")

@app.route("/bar", methods=["GET", "POST"])
def barpage():
    if request.method == "GET":
        if not session.get("last_bar"):
            redirect("/")
        bar_id=session["last_bar"]
        data = query.get_bar_data(bar_id)
        review_data = query.get_bar_reviews(bar_id)
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
            if not query.remove_review(r_id):
                redirect("/")
            if not bar_id:
                redirect("/")
        if user_id() and "rating" in request.form:
            if not query.check_if_already_reviewed(user_id(),bar_id):
                rating = request.form["rating"]
                comment = request.form["comment"]
                if not query.add_review(user_id(),bar_id,rating,comment):
                    return redirect("/")
        data = query.get_bar_data(bar_id)
        review_data = query.get_bar_reviews(bar_id)
        session["last_bar"]= bar_id
        return render_template("bar.html",bardata=data,reviews=review_data,weekLabels= weekdayList)

@app.route("/editbar", methods=["GET","POST"])
def editbar():
    if request.method =="GET":
        return render_template("editbar.html")
    if request.method == "POST":
        if "bar_id" in request.form:
            data = query.get_bar_data(request.form["bar_id"])
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
        if query.edit_bar(barname,description,address,open,close,user_id()):
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

def user_id():
    return session.get("user_id")

def delete_sessions():
    del session["user_id"]
    del session["username"]
    del session["admin"]
    del session["barowner"]

def login_user(username, password):
    user = query.get_user(username)
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
    query.add_user(username, password,barowner)
    return login_user(username, password)
