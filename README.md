SMS — Smart Management System
It is a web app built with Flask + SQLite + HTML/CSS/JS.
Backend: Python Flask, SQLite
Frontend: HTML, CSS, JavaScript
Security: bcrypt, flask-session, rate limiting, IDOR prevention, input validation
Database:
SQLite with 4 tables:
 `users` — auth and profile
 `tasks` — task management
 `learning_progress` — topic tracking
 `resources` — file uploads
Security:
- Passwords hashed with bcrypt
- Session-based auth
- Rate limiting on login/register
- IDOR prevention on all routes
- Input validation and logging
Progress:
Day 17 — Backend completed
Day 18 — Login, Register, Dashboard screens completed
Day 19 — Tasks, Learning Tracker completed
Day 20 — Resources, Admin Panel yet to complete
