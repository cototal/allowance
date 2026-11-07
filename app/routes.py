from datetime import date, datetime, time, timedelta
from decimal import Decimal
from urllib.parse import urlencode, urlparse

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import false, func

from app import db
from app.forms import DAYS, EntryForm, TaskForm
from app.models import Entry, Task, User
from app.security import verify_password
from app.view_models import EntryIndexViewModel, TaskFormViewModel


def register_routes(app):
    @app.get("/")
    def home():
        return redirect(url_for("entry_index"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("entry_index"))
        last_username = request.form.get("username", "")
        error = None
        if request.method == "POST":
            username = last_username.strip().lower()
            user = User.query.filter_by(username=username).first()
            if user is not None and verify_password(user, request.form.get("password", "")):
                db.session.commit()
                login_user(user, remember=bool(request.form.get("_remember_me")))
                target = request.args.get("next", "")
                parsed = urlparse(target)
                if target.startswith("/") and not parsed.netloc and not parsed.scheme:
                    return redirect(target)
                return redirect(url_for("entry_index"))
            error = "Invalid username or password."
        return render_template(
            "security/login.html", error=error, last_username=last_username
        )

    @app.post("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been signed out.", "info")
        return redirect(url_for("login"))

    @app.get("/entry")
    @login_required
    def entry_index():
        view_model = _build_entry_index_view_model()
        return render_template(
            "entry/index.html",
            view_model=view_model,
        ), 400 if view_model.search_errors else 200

    @app.route("/entry/new", methods=["GET", "POST"])
    @login_required
    def entry_new():
        form = EntryForm()
        errors = []
        if form.validate_on_submit():
            values = _entry_form_values(form)
            entry = Entry(user_id=current_user.id, **values)
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("entry_show", entry_id=entry.id))
        if request.method == "POST":
            errors = _form_errors(form)
        return render_template(
            "entry/form.html",
            entry=None,
            values={},
            form_data=request.form,
            errors=errors,
            title="New Entry",
        ), 400 if errors else 200

    @app.get("/entry/<int:entry_id>")
    @login_required
    def entry_show(entry_id):
        return render_template("entry/show.html", entry=_entry_or_404(entry_id))

    @app.route("/entry/<int:entry_id>/edit", methods=["GET", "POST"])
    @login_required
    def entry_edit(entry_id):
        entry = _entry_or_404(entry_id)
        form = EntryForm()
        errors = []
        if form.validate_on_submit():
            values = _entry_form_values(form)
            for key, value in values.items():
                setattr(entry, key, value)
            db.session.commit()
            return redirect(url_for("entry_index"))
        if request.method == "POST":
            errors = _form_errors(form)
        return render_template(
            "entry/form.html",
            entry=entry,
            values={},
            form_data=request.form,
            errors=errors,
            title="Edit Entry",
        ), 400 if errors else 200

    @app.post("/entry/<int:entry_id>/delete")
    @login_required
    def entry_delete(entry_id):
        entry = _entry_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        flash("Entry deleted.", "success")
        return redirect(url_for("entry_index"))

    @app.route("/task/new", methods=["GET", "POST"])
    @login_required
    def task_new():
        if Task.query.filter_by(user_id=current_user.id).first():
            flash("You may only set one task.", "warning")
            return redirect(url_for("entry_index"))
        form = TaskForm()
        errors = []
        if form.validate_on_submit():
            values = _task_form_values(form)
            task = Task(user_id=current_user.id, **values)
            db.session.add(task)
            db.session.commit()
            return redirect(url_for("entry_index"))
        if request.method == "POST":
            errors = _form_errors(form)
        view_model = _task_form_view_model(None, "New Task", errors)
        return render_template(
            "task/form.html",
            view_model=view_model,
        ), 400 if errors else 200

    @app.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
    @login_required
    def task_edit(task_id):
        task = db.session.get(Task, task_id) or abort(404)
        form = TaskForm()
        errors = []
        if form.validate_on_submit():
            values = _task_form_values(form)
            task.goal = values["goal"]
            task.reward = values["reward"]
            task.days = values["days"]
            db.session.commit()
            return redirect(url_for("entry_index"))
        if request.method == "POST":
            errors = _form_errors(form)
        view_model = _task_form_view_model(task, "Edit Task", errors)
        return render_template(
            "task/form.html",
            view_model=view_model,
        ), 400 if errors else 200

    @app.post("/task/<int:task_id>/delete")
    @login_required
    def task_delete(task_id):
        task = db.session.get(Task, task_id) or abort(404)
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted.", "success")
        return redirect(url_for("entry_index"))


def _entry_or_404(entry_id):
    return db.session.get(Entry, entry_id) or abort(404)


def _parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _task_form_view_model(task, title, errors):
    return TaskFormViewModel(
        task=task,
        title=title,
        goal=request.form.get("goal", task.goal if task else ""),
        reward=request.form.get("reward", task.reward if task else ""),
        selected_days=(
            request.form.getlist("days")
            if request.method == "POST"
            else task.days if task else []
        ),
        days=DAYS,
        errors=errors,
    )


def _build_entry_index_view_model():
    search_params = _entry_search_params()
    query, selected_user, search_errors = _entry_search_query(search_params)
    sortable = _entry_sortable_columns()
    sort = request.args.get("sort", "date")
    direction = request.args.get("direction", "desc").lower()
    query = _order_entries(query, sortable, sort, direction)
    entries, total, page, pages, page_numbers = _paginate_entries(query)
    balance, monthly_spending, task = _entry_summary()
    sort_urls, page_urls = _entry_index_urls(
        sortable, sort, direction, page_numbers
    )
    return EntryIndexViewModel(
        entries=entries,
        page=page,
        pages=pages,
        total=total,
        search_params=search_params,
        users=User.query.order_by(User.username).all(),
        selected_user=selected_user,
        balance=balance,
        monthly_spending=monthly_spending,
        task=task,
        sort=sort,
        direction=direction,
        sort_urls=sort_urls,
        page_urls=page_urls,
        page_numbers=page_numbers,
        search_errors=search_errors,
    )


def _entry_search_params():
    return {
        key.removeprefix("entry_search[")[:-1]: value
        for key, value in request.args.items()
        if key.startswith("entry_search[") and key.endswith("]")
    }


def _entry_search_query(search_params):
    query = Entry.query.join(User)
    search_errors = []
    selected_user = None
    user_value = search_params.get("userEquals", "").strip()
    if user_value:
        if user_value.isdigit():
            selected_user = db.session.get(User, int(user_value))
            query = query.filter(Entry.user_id == int(user_value))
        else:
            search_errors.append("Select a valid user.")

    for field in ("category", "payee", "notes"):
        value = search_params.get(f"{field}Contains", "").strip()
        if value:
            query = query.filter(getattr(Entry, field).ilike(f"%{value}%"))

    date_from = _parse_date(search_params.get("dateFrom"))
    date_to = _parse_date(search_params.get("dateTo"))
    for field, parsed in (("dateFrom", date_from), ("dateTo", date_to)):
        if search_params.get(field) and parsed is None:
            search_errors.append(
                f"Enter a valid {field.replace('date', 'date ').lower()}."
            )
    if date_from:
        query = query.filter(
            Entry.entry_date >= datetime.combine(date_from, time.min)
        )
    if date_to:
        query = query.filter(
            Entry.entry_date < datetime.combine(date_to + timedelta(days=1), time.min)
        )
    if search_errors:
        query = query.filter(false())
    return query, selected_user, search_errors


def _entry_sortable_columns():
    return {
        "username": User.username,
        "date": Entry.entry_date,
        "price": Entry.price,
        "payee": Entry.payee,
        "category": Entry.category,
        "notes": Entry.notes,
    }


def _order_entries(query, sortable, sort, direction):
    sort_column = sortable.get(sort, Entry.entry_date)
    return query.order_by(
        sort_column.asc() if direction == "asc" else sort_column.desc(),
        Entry.id.desc(),
    )


def _paginate_entries(query):
    total = query.count()
    per_page = 30
    pages = max((total + per_page - 1) // per_page, 1)
    page = max(request.args.get("page", 1, type=int), 1)
    page = min(page, pages)
    entries = query.offset((page - 1) * per_page).limit(per_page).all()
    page_numbers = list(range(max(1, page - 2), min(pages, page + 2) + 1))
    if page_numbers[0] > 1:
        page_numbers.insert(0, 1)
    if page_numbers[-1] < pages:
        page_numbers.append(pages)
    return entries, total, page, pages, page_numbers


def _entry_summary():
    balance_value = (
        db.session.query(func.sum(Entry.price))
        .filter(Entry.user_id == current_user.id)
        .scalar()
    )
    today = date.today()
    spending_value = (
        db.session.query(func.sum(Entry.price))
        .filter(
            Entry.user_id == current_user.id,
            Entry.price > 0,
            Entry.entry_date >= datetime.combine(today.replace(day=1), time.min),
            Entry.entry_date
            < datetime.combine(
                (today.replace(day=28) + timedelta(days=4)).replace(day=1),
                time.min,
            ),
        )
        .scalar()
    )
    task = Task.query.filter_by(user_id=current_user.id).first()
    return (
        -(balance_value or Decimal("0")),
        max(spending_value or Decimal("0"), Decimal("0")),
        task,
    )


def _entry_index_urls(sortable, sort, direction, page_numbers):
    endpoint_url = url_for("entry_index")
    sort_urls = {}
    for field in sortable:
        args = request.args.to_dict()
        args.update(
            sort=field,
            direction="asc" if sort == field and direction == "desc" else "desc",
            page="1",
        )
        sort_urls[field] = f"{endpoint_url}?{urlencode(args)}"

    page_urls = {}
    for number in page_numbers:
        args = request.args.to_dict()
        args["page"] = str(number)
        page_urls[number] = f"{endpoint_url}?{urlencode(args)}"
    return sort_urls, page_urls


def _entry_form_values(form):
    return {
        "entry_date": datetime.combine(form.entryDate.data, time.min),
        "price": form.price.data.quantize(Decimal("0.01")),
        "payee": form.payee.data or None,
        "category": form.category.data or None,
        "notes": form.notes.data or None,
    }


def _task_form_values(form):
    return {
        "goal": form.goal.data,
        "reward": form.reward.data,
        "days": form.days.data,
    }


def _form_errors(form):
    return [error for field_errors in form.errors.values() for error in field_errors]
