from database import get_db

db = get_db()
user = db.execute("SELECT email, role FROM users WHERE email = 'johanansj@gmail.com'").fetchone()
print(dict(user))