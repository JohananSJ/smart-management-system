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
-  Resource Upload — (in progress)
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

## Progress
-  Day 17 — Backend complete (completed)
-  Day 18 — Login, Register, Dashboard (completed)
-  Day 19 — Tasks, Learning Tracker (completed)
-  Day 20 — Resources, Admin Panel (yet to complete)