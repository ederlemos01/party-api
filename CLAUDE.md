# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django 6 REST API backed by PostgreSQL. Uses Django REST Framework for API endpoints. Project name is `core` (the Django project package); `users` is the first app. Language/timezone: `pt-br` / `America/Sao_Paulo`.

## Environment Setup

Requires a `.env` file at the project root (see `.gitignore` — it is excluded from git). Required variables:

```
SECRET_KEY=
DEBUG=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

Config is read via `python-decouple` (`core/settings.py`).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test users

# Run a single test case or method
python manage.py test users.tests.MyTestCase.test_something

# Django shell
python manage.py shell
```

## Architecture

```
core/           # Django project package (settings, root URLs, WSGI/ASGI)
users/          # User management app (models, views, serializers, tests)
manage.py
requirements.txt
```

Apps are registered in `INSTALLED_APPS` (`core/settings.py`). New apps follow the standard Django app layout: `models.py`, `views.py`, `serializers.py`, `urls.py`, `tests.py`, `admin.py`.

Root URL conf is `core/urls.py` — include each app's `urls.py` there via `include()`.

Database is PostgreSQL (`psycopg2-binary`). No SQLite fallback is configured.
