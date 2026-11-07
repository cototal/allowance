from datetime import datetime
from decimal import Decimal

from app import db
from app.models import Entry, Task


def pay_out_task(task):
    completed_days = len(task.days or [])
    task.days = []
    if completed_days <= 3:
        db.session.flush()
        return None

    allowance = (Decimal(completed_days) / Decimal(7)).quantize(Decimal("0.01"))
    entry = Entry(
        user=task.user,
        entry_date=datetime.now(),
        payee=task.user.username,
        price=allowance * Decimal("-10"),
        category="Allowance Task",
    )
    db.session.add(entry)
    db.session.flush()
    return entry
