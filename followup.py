import sqlite3
from datetime import datetime, timedelta
from app import send_email

HOURS = 24 

db = sqlite3.connect("clinic.db")
rows = db.execute(
    "SELECT rowid, name, email, treatment, created FROM enquiries "
    "WHERE status = 'New' AND followed_up = 0 AND email IS NOT NULL"
).fetchall()

sent = 0
for rowid, name, email, treatment, created in rows:
    received = datetime.strptime(created, "%d %b %Y %H:%M")
    if datetime.now() - received >= timedelta(hours=HOURS):
        send_email(
            email,
            "Still interested in " + treatment + "?",
            "Hi " + name + ",\n\n"
            + "We tried to reach you about your " + treatment + " enquiry. "
            + "Just reply to this email with a good time to call, "
            + "and we'll get you booked in.\n\n"
            + "Gurkha Cosmetics",
        )
        db.execute("UPDATE enquiries SET followed_up = 1 WHERE rowid = ?", (rowid,))
        sent += 1

db.commit()
db.close()
print("Follow-ups sent:", sent)