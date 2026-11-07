import os
from pathlib import Path

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.engine import make_url

# Extend the default LoginManager to include type hint for login_view
class AppLoginManager(LoginManager):
    login_view: str | None

db = SQLAlchemy()
login_manager = AppLoginManager()
csrf = CSRFProtect()


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(connection, _):
    if connection.__class__.__module__ == "sqlite3":
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(test_config=None):
    project_dir = Path(__file__).resolve().parent.parent
    (project_dir / "var").mkdir(exist_ok=True)
    app_env = os.environ.get("APP_ENV", "dev").lower()
    secret_key = (
        os.environ.get("SECRET_KEY")
        or os.environ.get("APP_SECRET")
        or (test_config or {}).get("SECRET_KEY")
    )
    if app_env in {"prod", "production"} and not secret_key:
        raise RuntimeError("SECRET_KEY must be configured in production.")

    app = Flask(
        __name__,
        template_folder=str(project_dir / "templates"),
        static_folder=str(project_dir / "public"),
    )
    database_url = os.environ.get(
        "DATABASE_URL", f"sqlite:///{(project_dir / 'var' / 'data.db').as_posix()}"
    )
    if database_url.startswith(("mysql://", "mysql+pymysql://")):
        parsed_url = make_url(database_url)
        query = dict(parsed_url.query)
        query.pop("serverVersion", None)
        database_url = parsed_url.set(
            drivername="mysql+pymysql", query=query
        )

    app.config.from_mapping(
        SECRET_KEY=secret_key or "dev-only-change-this-secret",
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        REMEMBER_COOKIE_DURATION=1209600,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=app_env in {"prod", "production"},
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Please sign in to continue."
    login_manager.login_message_category = "warning"
    csrf.init_app(app)

    from app import commands, models, routes  # noqa: F401

    commands.register_commands(app)
    routes.register_routes(app)

    @app.context_processor
    def inject_template_helpers():
        from datetime import datetime

        return {"now": datetime.now()}

    return app
