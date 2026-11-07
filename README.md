# Allowance

Allowance is a Flask application for a shared household ledger and personal
allowance tasks. It uses SQLAlchemy and can use SQLite locally or the existing
MySQL/MariaDB database.

## Run locally

Use Python 3.10 or newer:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
flask --app wsgi:app init-db
flask --app wsgi:app user-upsert <username>
flask --app wsgi:app run
```

By default, the database is stored in `var/data.db`. Set `DATABASE_URL` to
connect to MySQL/MariaDB, for example
`mysql://user:password@localhost:3306/app?charset=utf8mb4`. The MySQL URL is
handled through PyMySQL. Set `SECRET_KEY` to a strong, private value before
deploying; `APP_SECRET` is also accepted for existing Symfony deployments.

## Commands

`flask --app wsgi:app monthly` applies the monthly allowance to each user.
`flask --app wsgi:app task` processes and resets each user's allowance task.
`flask --app wsgi:app import-data <file> <user1-id> <user1-email> <user2-id>`
imports the legacy JSON export. `user-upsert` creates an account or optionally
changes its password.

## Existing database

The SQLAlchemy models retain the legacy `user`, `entry`, and `task` table and
column names. Point `DATABASE_URL` at the existing database; `init-db` creates
missing tables without replacing existing data. The login supports existing
Symfony bcrypt and Argon2 password hashes and upgrades them after successful
authentication.

## Tests

```powershell
python -m unittest discover -s tests
```
