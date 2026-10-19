import sqlite3
from flask import Flask, render_template, request, session, redirect 
app = Flask(__name__)
app.secret_key = "change-this-later"
def setup_database():
    db = sqlite3.connect("clinic.db")
    db.execute("CREATE TABLE IF NOT EXISTS enquiries ( name TEXT, phone TEXT, treatment TEXT)")
    db.commit()
    db.close()
setup_database()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/treatments")
def treatments():
    return "Facials, Botox and fillers, Skin rejuvenation"    

@app.route("/enquiry", methods=["POST"])
def enquiry():
    name = request.form["name"]
    phone = request.form["phone"]
    treatment = request.form["treatment"]
    db = sqlite3.connect("clinic.db")
    db.execute("INSERT INTO enquiries VALUES (?, ?, ?)", (name, phone, treatment))
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
    rows = db.execute("SELECT name, phone, treatment FROM enquiries"). fetchall()
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
app.run(debug=True, port=5001) 

