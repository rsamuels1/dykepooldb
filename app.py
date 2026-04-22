import os
import smtplib
import sqlite3
import uuid
from email.mime.text import MIMEText
from functools import wraps

from werkzeug.utils import secure_filename

from dotenv import load_dotenv
from flask import (Flask, g, jsonify, redirect, render_template,
                   request, session, url_for)

load_dotenv()

app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "img", "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(__file__), "pool.db")
)

RATINGS = {
    5: {"label": "LEGENDARY",   "stars": "🍒🍒🍒🍒🍒", "cls": "r5"},
    4: {"label": "PERFECT",     "stars": "🍒🍒🍒🍒",   "cls": "r4"},
    3: {"label": "PRETTY GOOD", "stars": "🍒🍒🍒",     "cls": "r3"},
    2: {"label": "DECENT",      "stars": "🍒🍒",       "cls": "r2"},
    1: {"label": "OKAY",        "stars": "🍒",         "cls": "r1"},
    0: {"label": "SKIP IT",     "stars": "ㄨ",         "cls": "r0"},
}

BATHROOM_OPTIONS = ["Gender-Neutral", "Gendered", "None"]


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    with open(os.path.join(os.path.dirname(__file__), "schema.sql")) as f:
        db.executescript(f.read())
    db.commit()
    db.close()


def migrate_db():
    """Add status column to databases that predate the review workflow."""
    db = sqlite3.connect(DATABASE)
    try:
        db.execute("ALTER TABLE venues ADD COLUMN status TEXT NOT NULL DEFAULT 'approved'")
        db.commit()
    except sqlite3.OperationalError:
        pass  # column already exists
    db.close()


def send_submission_email(venue_name, location, rating_int):
    """Send an alert email. Requires NOTIFY_EMAIL, SMTP_HOST, SMTP_USER, SMTP_PASS env vars."""
    notify_email = os.environ.get("NOTIFY_EMAIL")
    smtp_host    = os.environ.get("SMTP_HOST")
    smtp_user    = os.environ.get("SMTP_USER")
    smtp_pass    = os.environ.get("SMTP_PASS")
    smtp_port    = int(os.environ.get("SMTP_PORT", "587"))

    if not all([notify_email, smtp_host, smtp_user, smtp_pass]):
        print(f"[SUBMISSION] New pending venue: {venue_name} ({location}) — "
              "set NOTIFY_EMAIL, SMTP_HOST, SMTP_USER, SMTP_PASS to enable email alerts")
        return

    label = RATINGS.get(rating_int, {}).get("label", str(rating_int))
    body = (
        f"A new venue has been submitted and is waiting for your review.\n\n"
        f"  Venue:    {venue_name}\n"
        f"  Location: {location}\n"
        f"  Rating:   {label}\n\n"
        f"Review it at: {request.host_url}admin"
    )
    msg = MIMEText(body)
    msg["Subject"] = f"[Dyke Pool DB] New submission: {venue_name}"
    msg["From"]    = smtp_user
    msg["To"]      = notify_email

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception as e:
        print(f"[SUBMISSION] Email failed: {e}")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


# Run DB setup regardless of how the app is started (gunicorn or direct)
if not os.path.exists(DATABASE):
    init_db()
else:
    migrate_db()


# ── Public routes ────────────────────────────────────────────────────────────

@app.route("/pool-database")
def pool_database():
    db = get_db()
    venues = db.execute(
        "SELECT * FROM venues WHERE status = 'approved' ORDER BY created_at DESC"
    ).fetchall()
    prices = [r[0] for r in db.execute(
        "SELECT DISTINCT price_per_game FROM venues WHERE status = 'approved' ORDER BY price_per_game"
    ).fetchall()]
    return render_template("pool_database.html", venues=venues, ratings=RATINGS, prices=prices)


@app.route("/pool-database/<int:venue_id>")
def venue_detail(venue_id):
    db = get_db()
    venue = db.execute(
        "SELECT * FROM venues WHERE id = ? AND status = 'approved'", [venue_id]
    ).fetchone()
    if venue is None:
        return "Venue not found", 404
    return render_template("venue_detail.html", venue=venue, ratings=RATINGS)


@app.route("/submit", methods=["GET", "POST"])
@app.route("/contributor", methods=["GET", "POST"])
def submit():
    error = None
    if request.method == "POST":
        venue_name     = request.form.get("venue_name", "").strip()
        location       = request.form.get("location", "").strip()
        num_tables     = request.form.get("num_tables", "").strip()
        price_per_game = request.form.get("price_per_game", "").strip()
        bathroom_type  = request.form.get("bathroom_type", "").strip()
        rating         = request.form.get("rating", "").strip()
        notes          = request.form.get("notes", "").strip()

        if not all([venue_name, location, num_tables, price_per_game, bathroom_type, rating]):
            error = "All fields except notes and photo are required."
        else:
            photo_url = None
            photo = request.files.get("photo")
            if photo and photo.filename:
                if not allowed_file(photo.filename):
                    error = "Photo must be a JPG, PNG, WebP, or GIF."
                else:
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    ext = photo.filename.rsplit(".", 1)[1].lower()
                    filename = f"{uuid.uuid4().hex}.{ext}"
                    photo.save(os.path.join(UPLOAD_FOLDER, filename))
                    photo_url = f"img/uploads/{filename}"

            if not error:
                db = get_db()
                db.execute(
                    """INSERT INTO venues
                       (venue_name, location, num_tables, price_per_game,
                        bathroom_type, rating, notes, photo_url, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
                    [venue_name, location, int(num_tables), price_per_game,
                     bathroom_type, int(rating), notes, photo_url],
                )
                db.commit()
                send_submission_email(venue_name, location, int(rating))
                return redirect(url_for("submit_thanks"))

    return render_template(
        "submit.html",
        error=error,
        ratings=RATINGS,
        bathroom_options=BATHROOM_OPTIONS,
    )


@app.route("/submit/thanks")
def submit_thanks():
    return render_template("submit_thanks.html")


@app.route("/api/stats")
def api_stats():
    from datetime import datetime, timedelta
    db = get_db()
    venues = db.execute(
        "SELECT rating, location, created_at, num_tables, price_per_game, bathroom_type "
        "FROM venues WHERE status = 'approved'"
    ).fetchall()

    by_rating = {i: 0 for i in range(6)}
    cities = {}
    by_price = {}
    by_bathroom = {}
    year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    this_year = 0
    total_tables = 0

    for v in venues:
        by_rating[v["rating"]] = by_rating.get(v["rating"], 0) + 1
        cities[v["location"]] = cities.get(v["location"], 0) + 1
        if v["created_at"] and v["created_at"][:10] >= year_ago:
            this_year += 1
        total_tables += v["num_tables"] or 0
        price = v["price_per_game"] or "Unknown"
        by_price[price] = by_price.get(price, 0) + 1
        bathroom = v["bathroom_type"] or "Unknown"
        by_bathroom[bathroom] = by_bathroom.get(bathroom, 0) + 1

    ratings_sum = sum(v["rating"] for v in venues)
    avg_rating = round(ratings_sum / len(venues), 1) if venues else 0

    return jsonify({
        "total":        len(venues),
        "cities":       len(cities),
        "avg_rating":   avg_rating,
        "this_year":    this_year,
        "total_tables": total_tables,
        "by_rating":    by_rating,
        "by_city":      sorted(cities.items(), key=lambda x: -x[1]),
        "by_price":     sorted(by_price.items(), key=lambda x: -x[1]),
        "by_bathroom":  sorted(by_bathroom.items(), key=lambda x: -x[1]),
    })


# ── Admin routes ─────────────────────────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == os.environ.get("ADMIN_PASSWORD", ""):
            session["admin"] = True
            return redirect(url_for("admin"))
        error = "Incorrect password."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin():
    db = get_db()
    pending = db.execute(
        "SELECT * FROM venues WHERE status = 'pending' ORDER BY created_at DESC"
    ).fetchall()
    return render_template("admin.html", pending=pending, ratings=RATINGS)


@app.route("/admin/approve/<int:venue_id>", methods=["POST"])
@admin_required
def admin_approve(venue_id):
    db = get_db()
    db.execute("UPDATE venues SET status = 'approved' WHERE id = ?", [venue_id])
    db.commit()
    return redirect(url_for("admin"))


@app.route("/admin/reject/<int:venue_id>", methods=["POST"])
@admin_required
def admin_reject(venue_id):
    db = get_db()
    db.execute("DELETE FROM venues WHERE id = ? AND status = 'pending'", [venue_id])
    db.commit()
    return redirect(url_for("admin"))


if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    else:
        migrate_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
