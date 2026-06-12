from database import get_db
import sys

email = sys.argv[1] if len(sys.argv) > 1 else 'johanansj@gmail.com'

db = get_db()
cursor = db.execute("UPDATE users SET role = 'admin' WHERE email = ?", (email,))
db.commit()

if cursor.rowcount > 0:
    print(f"Success! {email} is now admin.")
else:
    print(f"No user found with email: {email}")