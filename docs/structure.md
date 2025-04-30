# /forge/docs/structure.md

# ⚙️ WarriorsForge Project Structure

This document defines the intended architecture for WarriorsForge.
Use it to prevent logic drift, folder misuse, and architectural spaghetti.

---

## /app/
> (Optional) Scripts, CLI tools, or platform adapters.

## /backend/
> All Flask logic lives here: models, views, services, routing.

- `__init__.py` — App factory
- `models/` — SQLAlchemy ORM models (User, Task, Deep Work, etc.)
- `routes/` — Blueprints for auth, core, calendar, AI
- `services/` — Custom logic like ForgeMind AI
- `templates/` — Jinja2 views (linked to frontend directory)
- `extensions.py` — Central extension init (db, csrf, login_manager, migrate)

## /frontend/
> All UI assets
- `static/` — CSS, JS, images
- `templates/` — HTML views consumed by Flask

## Project Root
- `config.py` — Configuration class
- `app.py` — Entrypoint (optional if using gunicorn/Procfile)
- `init_db.py` — Bootstrap DB
- `.env.example` — Env template
- `requirements.txt`, `README.md`, `.gitignore`, `Procfile`


---

# ☑️ Core Principles
- Clean separation of concerns
- AI logic = service layer, not views
- Authentication = modular and optional
- Deployable to Render Free Tier
- Supports future move to async (if needed)


---

# ✅ Development Checklist (Tactical)

## 🔧 Extensions
- [x] SQLAlchemy (`db`)
- [x] Flask-Migrate (`migrate`)
- [x] CSRFProtect (`csrf`)
- [x] LoginManager (`login_manager`)

## ⚙️ App Init (backend/__init__.py)
- [x] Load environment via dotenv
- [x] Register extensions
- [x] Register Blueprints
- [x] Setup login view + user_loader
- [x] Template path linked to `/frontend`

## 🛠️ Models
- [x] `User`
- [ ] `Task`
- [ ] `CalendarEvent`
- [ ] `DeepWorkSession`

## 🔌 Routes
- [x] `/` (core dashboard)
- [x] `/calendar`
- [x] `/forge_ai/checkin`
- [ ] `/login`, `/logout`, `/register`
- [ ] `/tasks` (CRUD)

## 🧠 Services
- [x] `ForgeMindAI` exists in `/services/`
- [ ] Supports user performance tracking
- [ ] Brutality behavior applies penalties

## 📦 Misc
- [x] `.env.example` exists
- [x] `README.md` exists
- [x] `init_db.py` runs db.create_all
- [ ] Add `migrations/` directory for versioning
