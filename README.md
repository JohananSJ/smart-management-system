# SMS — Smart Management System

A web app built with Flask + SQLite + HTML/CSS/JS.

## Tech Stack
- Backend: Python Flask, SQLite
- Frontend: HTML, CSS, JavaScript (no frameworks)
- Security: bcrypt, flask-session, rate limiting, IDOR prevention, input validation

## Features
-  Login & Register with password strength meter
-  Dashboard with stats, streak tracker, recent activity
-  Tasks — Kanban board (To Do, In Progress, Done)
-  Learning Tracker — topic progress, notes
-  Resource Upload — drag & drop, file cards, filters
-  Admin Panel — (in progress)

## Database
SQLite with 4 tables:
- `users` — auth and profile
- `tasks` — task management
- `learning_progress` — topic tracking
- `resources` — file uploads

## Security
- Passwords hashed with bcrypt
- Session-based auth
- Rate limiting on login/register
- IDOR prevention on all routes
- Input validation and logging

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

## Progress
- Day 17 — Backend (completed)
- Day 18 — Login, Register, Dashboard (completed)
- Day 19 — Tasks, Learning Tracker, dot field (completed)
- Day 20 — Resources page, dashboard fixes (completed)
- Day 21 — Admin Panel (yet to complete)

## Notes
- App runs on port 5001 (`flask run --port 5001`)
- Port 5000 has Windows cache issue