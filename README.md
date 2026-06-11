# SMS — Smart Management System

A full-stack web application built with Flask, SQLite, and vanilla HTML/CSS/JS.

## Tech Stack
- Backend: Python Flask, SQLite
- Frontend: HTML, CSS, JavaScript (no frameworks)
- Security: bcrypt, Flask-Session, rate limiting, IDOR prevention, input validation

## Features
- Login and Register with password strength meter
- Dashboard with stats, streak tracker and recent activity
- Tasks — Kanban board (To Do, In Progress, Done)
- Learning Tracker — topic progress tracking and notes
- Resource Upload — drag and drop, file cards, filters
- Admin Panel — user management, system stats

## Database
SQLite with 4 tables:
- `users` — authentication and profile
- `tasks` — task management
- `learning_progress` — topic tracking
- `resources` — file uploads

## Security
- Passwords hashed with bcrypt
- Session-based authentication
- Rate limiting on login and register
- IDOR prevention on all routes
- Input validation and sanitization
- Activity logging

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | Login |
| POST | `/logout` | Logout |
| GET | `/tasks` | Get all tasks |
| POST | `/tasks` | Create task |
| PUT | `/tasks/<id>` | Update task |
| DELETE | `/tasks/<id>` | Delete task |
| GET | `/progress` | Get all topics |
| POST | `/progress` | Add topic |
| PUT | `/progress/<id>` | Update topic |
| DELETE | `/progress/<id>` | Delete topic |
| POST | `/upload` | Upload file |
| GET | `/api/resources` | Get all files |
| DELETE | `/api/resources/<id>` | Delete file |
| GET | `/api/admin/stats` | Get system stats |
| GET | `/api/admin/users` | Get all users |
| DELETE | `/api/admin/users/<id>` | Delete user |

## Pages
| Route | Page |
|-------|------|
| `/login` | Login |
| `/register` | Register |
| `/dashboard` | Dashboard |
| `/tasks-board` | Tasks Kanban |
| `/learning` | Learning Tracker |
| `/resources` | Resource Upload |
| `/admin` | Admin Panel |

## Running the App
```bash
pip install -r requirements.txt
python -m flask run --port 5001
```

## Progress
- Day 17 — Backend complete
- Day 18 — Login, Register, Dashboard complete
- Day 19 — Tasks, Learning Tracker complete
- Day 20 — Resources page complete
- Day 21 — Admin Panel complete

## Notes
- App runs on port 5001 due to Windows port 5000 cache issue
- Admin access requires role to be set to admin in the database
- Port 5000 has Windows cache issue
- SQLite database file is excluded from version control