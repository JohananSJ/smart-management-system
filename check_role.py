from database import get_db
import sys

email = sys.argv[1] if len(sys.argv) > 1 else 'johanansj@gmail.com'

db = get_db()
user = db.execute("SELECT email, role FROM users WHERE email = ?", (email,)).fetchone()

if user:
    print(dict(user))
else:
    print(f"No user found with email: {email}")