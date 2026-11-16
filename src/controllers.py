"""Controller: HTTP input/output and orchestration; no SQL or HTML strings."""
import hmac
import secrets
from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

pages = Blueprint("pages", __name__)


def stock(): return current_app.extensions["stock"]


def render(error=None, status=200):
    session.setdefault("csrf", secrets.token_urlsafe(32))
    return render_template("index.html", seeds=stock().list_seeds(), reservations=stock().list_reservations(),
                           csrf=session["csrf"], error=error), status


@pages.before_request
def check_csrf():
    if request.method == "POST":
        submitted = request.form.get("csrf", "")
        expected = session.get("csrf", "")
        if not expected or not hmac.compare_digest(submitted, expected): return render("Vormi seanss aegus. Proovi uuesti.", 400)


@pages.get("/")
def index(): return render()


@pages.post("/seeds")
def add():
    try:
        quantity = int(request.form.get("quantity", ""))
        stock().add_seed(request.form.get("name", ""), quantity)
    except ValueError as error:
        return render("Kontrolli nime ja mittenegatiivset täisarvulist kogust. " + str(error), 400)
    return redirect(url_for("pages.index"), code=303)


@pages.post("/reservations")
def reserve():
    try:
        stock().reserve(request.form.get("seedId", ""), int(request.form.get("quantity", "")))
    except ValueError as error:
        return render("Broneeringut ei tehtud. " + str(error), 400)
    return redirect(url_for("pages.index"), code=303)


@pages.post("/reservations/<reservation_id>/cancel")
def cancel(reservation_id):
    try: stock().cancel(reservation_id)
    except ValueError as error: return render(str(error), 400)
    return redirect(url_for("pages.index"), code=303)
