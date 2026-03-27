<div align="center">

# 🌟 StarLight - Share Your Stories with the Universe

A modern blogging platform for writing, publishing, and community-driven reading.

![Angular](https://img.shields.io/badge/Angular-15+-dd0031?style=flat&logo=angular&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-black?style=flat&logo=flask&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-Frontend-3178c6?style=flat&logo=typescript&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-d71f00?style=flat&logo=sqlalchemy&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Sessions-000000?style=flat&logo=jsonwebtokens&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952b3?style=flat&logo=bootstrap&logoColor=white)

</div>

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Stack](#stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)

## Overview

StarLight is a full-stack blogging app with a polished reading experience, a rich post editor, authenticated profiles, and engagement features such as comments and likes. The repository is split into a Flask backend and an Angular frontend, which keeps the app easy to run and easy to extend.

## Features

- Rich text publishing with TinyMCE-powered post composition.
- User registration, login, profile management, and JWT-backed sessions.
- Comments, likes, and post feeds for community engagement.
- Category/community browsing with separate views for personal and public content.
- Responsive UI with a glassmorphism-inspired visual system.

## Stack

- Frontend: Angular, TypeScript, RxJS, Bootstrap, SCSS.
- Backend: Flask, Flask-CORS, Flask-Login, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Session.
- Data: SQLite via SQLAlchemy models and Alembic migrations.

## Quick Start

### Backend

```bash
cd starlight-backend
pip install flask flask-cors flask-login flask-sqlalchemy flask-migrate flask-jwt-extended flask-session
python app.py
```

The backend runs on `http://localhost:8080`.

### Frontend

```bash
cd starlight-ng
npm install
npx ng serve --port 4200
```

The frontend runs on `http://localhost:4200`.

## Project Structure

```text
.
├── starlight-backend/
│   ├── app.py            # Flask application and API routes
│   ├── models.py         # SQLAlchemy models
│   └── migrations/       # Database migration history
├── starlight-ng/
│   ├── src/app/
│   │   ├── pages/        # Homepage, posts, auth, profile, communities
│   │   ├── services/     # API and auth services
│   │   └── components/   # Shared UI components
│   └── src/assets/img/   # Branding and profile assets
└── MODERNIZATION_SUMMARY.md
```
