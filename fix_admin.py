from database import get_db

db = get_db()
db.execute("UPDATE users SET role = 'admin' WHERE email = 'johanansj@gmail.com'")
db.commit()
print("Done!")