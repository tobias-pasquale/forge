# 🔥 Forge – Deep Work Tracker

**Forge** is a lightweight productivity app designed to help individuals track their Deep Work sessions and build disciplined focus over time. Whether you're studying, coding, writing, or creating—Forge helps you quantify and improve the quality of your attention.

---

## 📦 Features

- Log sessions with:
  - 🕒 **Duration** (in hours)
  - 🧠 **Depth** (1–5 scale)
  - 🚀 **Impact** (1–5 scale)
  - 📁 **Category** (project, topic, or type of work)
  - 📝 **Notes** for context and reflection
- View a history of past sessions
- Clean, responsive interface using Flask & Jinja2
- SQLite-backed database for fast, local use

---

## 📁 Project Structure

/forge/                            # Project root (version-controlled)
├── app.py                         # Entrypoint for production/gunicorn
├── config.py                      # App settings (prod/dev/test modes)
/backend/                          # All Flask logic lives here
│   ├── __init__.py                # App factory pattern
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── calendar_event.py
│   │   └── deep_work.py
│   ├── routes/                    # Blueprints
│   │   ├── core.py
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   ├── calendar.py
│   │   └── forge_ai.py
│   ├── services/                  # ForgeMind, AI logic, integrations
│   │   └── forgemind.py
│   ├── templates/                 # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   └── calendar.html
│   └── extensions.py              # LoginManager, DB, etc.
│
/frontend/                         # Static & design assets
│   ├── static/                    # CSS, JS, fonts, assets
│   │   ├── styles.css
│   │   └── darkmode.css
│   └── js/                        # Optional future Vue/React/PureJS
│       └── forge_ai.js
│
/migrations/                       # Flask-Migrate directory
/env/                              # Git-ignored virtual env (dev only)
.gitignore
.env.example
init_db.py                         # DB seeding/setup
Procfile                           # For Render deployment
README.md
requirements.txt




# Forge Development Transcript

This document captures the full development journey of the Forge application through conversations with ChatGPT.

---

## 🔧 Setup and Initialization

**Prompt:**
> I would like to work on my Deep Work App. What should I call it?

**ChatGPT Response:**
We explored several names and settled on **Forge**, symbolizing a place of transformation and productivity.

**Prompt:**
> Now, let's build it. You can scaffold and give me the starter code.

[ChatGPT responded with a starter Flask application layout, including `app.py`, routes, templates, and database setup.]

**Prompt:**
> I have the files set up, how can I push this to my github now? I am using VSCode

[ChatGPT explained how to initialize a Git repo, commit files, and push to GitHub.]

---

## 🏗️ Core Functionality

**Prompt:**
> It gave me a lot of errors. Here they are:
(sqlalchemy.exc.OperationalError: no such table: session...)

ChatGPT walked through how to properly initialize the database and avoid circular imports. 

**Prompt:**
> When I try to run the app with python run.py ... I am getting a 404 error now

ChatGPT helped debug route registration issues, verified blueprints, and helped wire up the index view properly.

---

## 🔐 Authentication

**Prompt:**
> I want to add the ability for other users to create accounts and have their own forge

[ChatGPT guided the creation of the `User` model, registration and login forms, and login-protected routes.]

**Prompt:**
> I was able to register and login successfully.

🎉 Milestone reached.

---

## 📋 To-Do Tracker

**Prompt:**
> I want to add the page for my to-do list. I would like to have ChatGPT integrated so that it can help me with tracking and optimizations as well as sharing encouragement when needed.

**Prompt:**
> 1. Checkboxes
> 2. Yes and Yes
> 3. Yes

ChatGPT generated a `/todo` route, form handling, streak tracking logic, and OpenAI integration.

**Prompt:**
> Can you go ahead and refactor the todo.html to use Flask-WTF?

**Prompt:**
> This is my forms.py file. Will that work?

ChatGPT integrated Flask-WTF across the to-do page, added CSRF protection, and created the `ToDoForm` and `AskGptForm`.

---

## 🎨 UI Design

**Prompt:**
> Let's give it a more modern sleek look too, I want to keep the FORGE feel, but modernize it.

**Prompt:**
> Hover Forge glow effect

**Prompt:**
> Would be awesome if we could make it look like the user's mouse was smoking for 1–2 seconds after hovering over FORGE

ChatGPT provided full Bootstrap 5 integration with custom CSS and JavaScript to match the Forge aesthetic.

---

## 🚀 Deployment

**Prompt:**
> If I want to eventually host this, somewhere like Heroku. Do I need to use a different kind of DB?

ChatGPT suggested PostgreSQL and then guided a successful deployment to Render, helping resolve database connection and environment variable issues.

---

## 📊 Metrics and Productivity Tracking

**Prompt:**
> I have attached my current personal growth tracker. Can we get this data loaded into the database?

ChatGPT parsed Excel data and preloaded monthly productivity history into the database.

**Prompt:**
> I would like it to help me track my daily to-dos like you do...

Forge now supports a hybrid of tracked deep work sessions and actionable to-dos with motivational feedback.

---

## 📜 Full Prompt Log Available

All the prompts above were real-time user entries. This document captures their content directly as typed by the user.

If you'd like a raw log of *only* the prompts without formatting or a JSON array of prompt logs for audit/training purposes, just let me know.

---

**Maintained by:** Tobias Pasquale

**App Name:** Forge – Deep Work Tracker

**Tech Stack:** Flask, PostgreSQL, Bootstrap 5, OpenAI API

**Status:** 🛠️ Actively developed

