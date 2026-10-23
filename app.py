import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, session, redirect 
app = Flask(__name__)
app.secret_key = "change-this-later"
def setup_database():
    db = sqlite3.connect("clinic.db")
    db.execute("CREATE TABLE IF NOT EXISTS enquiries (name TEXT, phone TEXT, treatment TEXT, created TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS sales (item TEXT, amount REAL, created TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS costs (item TEXT, amount REAL, created TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS treatments (name TEXT, price TEXT)")
    db.commit()
    db.close()
setup_database()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/treatments")
def treatments():
    db = sqlite3.connect("clinic.db")
    rows = db.execute("SELECT name, price FROM treatments").fetchall()
    db.close()
    return render_template("treatments.html", rows=rows)    

@app.route("/enquiry", methods=["POST"])
def enquiry():
    name = request.form["name"]
    phone = request.form["phone"]
    treatment = request.form["treatment"]
    created = datetime.now().strftime("%d %b %Y %H:%M")
    db = sqlite3.connect("clinic.db")
    db.execute("INSERT INTO enquiries VALUES (?, ?, ?, ?)", (name, phone, treatment, created))
    db.commit()
    db.close()
    return "Thanks " + name + ", we'll call you soon about " + treatment

@app.route("/contact")
def contact():
    return "Call on us 000000000 or email us at hello@gurkhacosmetics.co.uk"    

@app.route("/enquiries")
def enquiries():
    if not session.get("logged_in"):
        return redirect("/login")
    db = sqlite3.connect("clinic.db")
    rows = db.execute("SELECT name, phone, treatment, created FROM enquiries ORDER BY rowid DESC").fetchall()
    db.close()
    return render_template("enquiries.html", rows=rows)    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == "clinic123":
            session["logged_in"] = True
            return redirect("/enquiries")
        return "Wrong password"
    return render_template("login.html")

@app.route("/manage", methods=["GET", "POST"])
def manage():
    if not session.get("logged_in"):
        return redirect("/login")
    db = sqlite3.connect("clinic.db")
    if request.method == "POST":
        db.execute("INSERT INTO treatments VALUES (?, ?)", (request.form["name"], request.form["price"]))
        db.commit()
    treatments = db.execute("SELECT rowid, name, price FROM treatments").fetchall()
    db.close()
    return render_template("manage.html", treatments=treatments)

@app.route("/stats")
def stats():
    if not session.get("logged_in"):
        return redirect("/login")
    db = sqlite3.connect("clinic.db")
    total = db.execute("SELECT COUNT(*) FROM enquiries").fetchone()[0]
    db.close()
    return "Total enquriries: " + str(total)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    if not session.get("logged_in"):
        return redirect("/login")
    db = sqlite3.connect("clinic.db")
    db.execute("DELETE FROM treatments WHERE rowid = ?", (id,))
    db.commit()
    db.close()
    return redirect("/manage")

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    if not session.get("logged_in"):
        return redirect("/login")
    db = sqlite3.connect("clinic.db")
    db.execute("UPDATE treatments SET price = ? WHERE rowid = ?", (request.form["price"], id))
    db.commit()
    db.close()
    return redirect("/manage")    

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/money", methods=["GET", "POST"])
def money():
    if not session.get("logged_in"):
        return redirect("/login")
    db = sqlite3.connect("clinic.db")
    if request.method == "POST":
        created = datetime.now().strftime("%d %b %Y")
        db.execute("INSERT INTO sales VALUES (?, ?, ?)", (request.form["item"], float(request.form["amount"]), created))
        db.commit()
    sales = db.execute("SELECT item, amount, created FROM sales ORDER BY rowid DESC").fetchall()
    total = db.execute("SELECT SUM(amount) FROM sales").fetchone()[0] or 0
    costs = db.execute("SELECT item, amount, created FROM costs ORDER BY rowid DESC").fetchall()
    cost_total = db.execute("SELECT SUM(amount) FROM costs").fetchone()[0] or 0
    db.close()
    return render_template("money.html", sales=sales, total=total, costs=costs, cost_total=cost_total)
      
@app.route("/add-cost", methods=["POST"])
def add_cost():
    if not session.get("logged_in"):
        return redirect("/login")
    db = sqlite3.connect("clinic.db")
    created = datetime.now().strftime("%d %b %Y")
    db.execute("INSERT INTO costs VALUES (?, ?, ?)", (request.form["item"], float(request.form["amount"]), created))
    db.commit()
    db.close()
    return redirect("/money")
app.run(debug=True, port=5001) 

