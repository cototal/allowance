from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    SelectMultipleField,
    StringField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    Optional,
    ValidationError,
)

DAYS = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]


def _strip(value: str | None) -> str | None:
    return value.strip() if value else value


def _validate_price(_form: FlaskForm, field: DecimalField) -> None:
    value = field.data
    if value is None:
        return
    if (
        not value.is_finite()
        or value != value.quantize(Decimal("0.01"))
        or abs(value) >= Decimal("100000000")
    ):
        raise ValidationError("Enter a valid price with up to two decimal places.")


class EntryForm(FlaskForm):
    entryDate = DateField(
        "Entry date",
        format="%Y-%m-%d",
        validators=[InputRequired(message="Enter a valid entry date.")],
    )
    price = DecimalField(
        "Price",
        places=None,
        validators=[
            InputRequired(message="Enter a valid price with up to two decimal places."),
            _validate_price,
        ],
    )
    payee = StringField(
        "Payee",
        filters=[_strip],
        validators=[
            Optional(),
            Length(max=255, message="Payee must be 255 characters or fewer."),
        ],
    )
    category = StringField(
        "Category",
        filters=[_strip],
        validators=[
            Optional(),
            Length(max=255, message="Category must be 255 characters or fewer."),
        ],
    )
    notes = TextAreaField("Notes", filters=[_strip])


class TaskForm(FlaskForm):
    goal = StringField(
        "Goal",
        filters=[_strip],
        validators=[
            DataRequired(message="Enter a goal of 1 to 255 characters."),
            Length(max=255, message="Enter a goal of 1 to 255 characters."),
        ],
    )
    reward = StringField(
        "Reward",
        filters=[_strip],
        validators=[
            DataRequired(message="Enter a reward of 1 to 255 characters."),
            Length(max=255, message="Enter a reward of 1 to 255 characters."),
        ],
    )
    days = SelectMultipleField(
        "Days",
        choices=[(day, day) for day in DAYS],
        validate_choice=False,
        filters=[lambda values: list(dict.fromkeys(values or []))],
    )

    def validate_days(self, field: SelectMultipleField) -> None:
        if any(day not in DAYS for day in field.data or []):
            raise ValidationError("Select valid days.")
