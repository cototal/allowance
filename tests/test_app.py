from datetime import datetime
from decimal import Decimal
import unittest

from app import create_app, db
from app.models import Entry, Task, User


class AllowanceAppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-key",
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "WTF_CSRF_ENABLED": False,
            }
        )
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.user = User(username="alex", roles=[])
        self.user.set_password("correct horse")
        db.session.add(self.user)
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def login(self):
        return self.client.post(
            "/login", data={"username": "alex", "password": "correct horse"}
        )

    def test_login_protects_ledger_and_rejects_bad_password(self):
        self.assertEqual(self.client.get("/entry").status_code, 302)
        response = self.client.post(
            "/login", data={"username": "alex", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid username or password", response.data)
        self.assertEqual(self.login().status_code, 302)
        self.assertEqual(self.client.get("/entry").status_code, 200)

    def test_post_requires_csrf_token(self):
        self.app.config["WTF_CSRF_ENABLED"] = True
        response = self.client.post(
            "/login", data={"username": "alex", "password": "correct horse"}
        )
        self.assertEqual(response.status_code, 400)

    def test_entry_create_filter_and_delete(self):
        self.login()
        response = self.client.post(
            "/entry/new",
            data={
                "entryDate": "2026-03-10",
                "price": "12.34",
                "payee": "Market",
                "category": "Food",
                "notes": "Groceries",
            },
        )
        self.assertEqual(response.status_code, 302)
        entry = Entry.query.one()
        self.assertEqual(entry.user_id, self.user.id)
        self.assertEqual(entry.price, Decimal("12.34"))
        self.assertEqual(entry.entry_date, datetime(2026, 3, 10))
        response = self.client.get(
            "/entry?entry_search%5BcategoryContains%5D=Foo"
        )
        self.assertIn(b"Market", response.data)
        self.assertIn(
            b"entry_search%5BcategoryContains%5D=Foo&amp;sort=username",
            response.data,
        )
        self.assertEqual(
            self.client.post(f"/entry/{entry.id}/delete").status_code, 302
        )
        self.assertEqual(Entry.query.count(), 0)

    def test_entry_validation_rejects_extra_decimal_places(self):
        self.login()
        response = self.client.post(
            "/entry/new",
            data={"entryDate": "2026-03-10", "price": "1.239"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"valid price", response.data)
        self.assertEqual(Entry.query.count(), 0)

    def test_task_creation_and_single_task_rule(self):
        self.login()
        response = self.client.post(
            "/task/new", data={"goal": "Read", "reward": "A book"}
        )
        self.assertEqual(response.status_code, 302)
        task = Task.query.one()
        self.assertEqual(task.user_id, self.user.id)
        self.assertEqual(task.days, [])
        self.assertIn(b"Read", self.client.get("/entry").data)
        self.assertEqual(
            self.client.get("/task/new").headers["Location"], "/entry"
        )

    def test_task_validation_rejects_invalid_days(self):
        self.login()
        response = self.client.post(
            "/task/new",
            data={"goal": "Read", "reward": "A book", "days": ["Funday"]},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Select valid days", response.data)
        self.assertEqual(Task.query.count(), 0)

    def test_task_edit_view_model_uses_task_and_submitted_values(self):
        self.login()
        task = Task(user=self.user, goal="Read", reward="A book", days=["Monday"])
        db.session.add(task)
        db.session.commit()

        response = self.client.get(f"/task/{task.id}/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'value="Monday" checked', response.data)
        self.assertIn(b'value="Read"', response.data)

        response = self.client.post(
            f"/task/{task.id}/edit",
            data={"goal": "", "reward": "New reward", "days": ["Tuesday"]},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'value="New reward"', response.data)
        self.assertIn(b'value="Tuesday" checked', response.data)

    def test_monthly_command_applies_allowance(self):
        result = self.app.test_cli_runner().invoke(args=["monthly"])
        self.assertEqual(result.exit_code, 0, result.output)
        entry = Entry.query.one()
        self.assertEqual(entry.price, Decimal("-100.00"))
        self.assertEqual(entry.category, "Allowance")

    def test_model_constructors_preserve_sqlalchemy_behavior(self):
        user = User(username="sam", roles=[], password="hash")
        entry = Entry(user=user, entry_date=datetime(2026, 3, 10), price=Decimal("1.00"))
        task = Task(user=user, goal="Read", reward="A book", days=[])
        self.assertIs(entry.user, user)
        self.assertIs(task.user, user)
        self.assertIn(entry, user.entries)
        self.assertIn(task, user.tasks)
        for model in (User, Entry, Task):
            with self.subTest(model=model.__name__):
                self.assertIsNotNone(model())
                with self.assertRaisesRegex(TypeError, "invalid_keyword"):
                    type.__call__(model, invalid_keyword="value")


if __name__ == "__main__":
    unittest.main()
