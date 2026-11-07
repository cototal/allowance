import json
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import click
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app import db
from app.models import Entry, Task, User
from app.services import pay_out_task


def register_commands(app):
    @app.cli.command("init-db")
    def init_db():
        """Create any missing application tables."""
        db.create_all()
        click.echo("Database tables are ready.")

    @app.cli.command("monthly")
    def monthly():
        """Apply the monthly allowance to every user."""
        users = User.query.order_by(User.id).all()
        for user in users:
            db.session.add(
                Entry(
                    user=user,
                    entry_date=datetime.now(),
                    payee=user.username,
                    category="Allowance",
                    price=Decimal("-100.00"),
                )
            )
        db.session.commit()
        click.echo(f"Allowance applied to {len(users)} users.")

    @app.cli.command("task")
    def task():
        """Pay out eligible allowance tasks and reset their tracked days."""
        tasks = Task.query.order_by(Task.id).all()
        paid = sum(pay_out_task(item) is not None for item in tasks)
        db.session.commit()
        click.echo(f"Allowance task paid out to {paid} users.")

    @app.cli.command("import-data")
    @click.argument("filename", type=click.Path(exists=True, dir_okay=False, path_type=Path))
    @click.argument("user1id", type=int)
    @click.argument("user1email")
    @click.argument("user2id", type=int)
    def import_data(filename, user1id, user1email, user2id):
        """Import entries from JSON using the legacy user-selection rules."""
        try:
            records = json.loads(filename.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise click.ClickException(f"Could not read import file: {error}") from error
        if not isinstance(records, list):
            raise click.ClickException("The import file must contain a JSON array.")

        user1 = db.session.get(User, user1id)
        user2 = db.session.get(User, user2id)
        if user1 is None or user2 is None:
            raise click.ClickException("Both specified users must exist.")

        entries = []
        for index, record in enumerate(records, start=1):
            try:
                owner = user1 if record["user"] == user1email else user2
                entry_date = datetime.strptime(record["entry_date"], "%Y-%m-%d")
                price = Decimal(str(record["price"]))
                rounded_price = price.quantize(Decimal("0.01"))
                if (
                    not price.is_finite()
                    or price != rounded_price
                    or abs(rounded_price) >= Decimal("100000000")
                ):
                    raise ValueError("price must have no more than two decimal places")
                entries.append(
                    Entry(
                        user=owner,
                        entry_date=entry_date,
                        price=rounded_price,
                        category=record.get("category"),
                        payee=record.get("payee"),
                        notes=re.sub(r"</?p>", "", record.get("notes") or ""),
                    )
                )
            except (KeyError, TypeError, ValueError, InvalidOperation) as error:
                raise click.ClickException(
                    f"Invalid record {index}: {error}"
                ) from error

        db.session.add_all(entries)
        try:
            db.session.commit()
        except (IntegrityError, ValueError) as error:
            db.session.rollback()
            raise click.ClickException(f"Import failed: {error}") from error
        click.echo(f"{len(entries)} records imported.")

    @app.cli.command("user-upsert")
    @click.argument("username")
    def user_upsert(username):
        """Create a user or change an existing user's password."""
        username = username.lower()
        user = User.query.filter_by(username=username).first()
        if user and not click.confirm("User found, change password?", default=False):
            return
        if user is None:
            user = User(username=username, roles=[])
            db.session.add(user)
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
        user.password = generate_password_hash(password)
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise click.ClickException(f"Could not save user: {error}") from error
        click.echo(f"{username} created or updated.")
