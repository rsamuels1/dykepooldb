import os
import smtplib
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from functools import wraps

import psycopg2
import psycopg2.errors
import psycopg2.extras
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


DATABASE_URL = os.environ.get("DATABASE_URL", "")
# Railway (and some other hosts) provide postgres:// but psycopg2 requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

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
        db = g._database = psycopg2.connect(DATABASE_URL)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    with open(os.path.join(os.path.dirname(__file__), "schema.sql")) as f:
        sql = f.read()
    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if stmt:
            cur.execute(stmt)
    conn.commit()
    cur.close()
    conn.close()


def migrate_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE venues ADD COLUMN status TEXT NOT NULL DEFAULT 'approved'")
        conn.commit()
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def _table_exists():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('public.venues')")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] is not None


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


_db_initialized = False


def ensure_db_initialized():
    """Initialize the database lazily on first use, with error handling.

    Returns True if the database is ready, False if the connection failed.
    Called explicitly by routes that need the database rather than on every
    request, so the app can start and serve non-DB routes immediately.
    """
    global _db_initialized
    if _db_initialized:
        return True
    try:
        if not _table_exists():
            init_db()
        else:
            migrate_db()
        _db_initialized = True
        return True
    except Exception as e:
        print(f"[DB] Database initialization failed: {e}")
        return False


# ── Public routes ────────────────────────────────────────────────────────────

@app.route("/pool-database")
def pool_database():
    if not ensure_db_initialized():
        return "Database unavailable — please try again shortly.", 503
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM venues WHERE status = 'approved' ORDER BY created_at DESC")
    venues = cur.fetchall()
    cur.execute(
        "SELECT DISTINCT price_per_game FROM venues WHERE status = 'approved' ORDER BY price_per_game"
    )
    prices = [r["price_per_game"] for r in cur.fetchall()]
    return render_template("pool_database.html", venues=venues, ratings=RATINGS, prices=prices)


@app.route("/pool-database/<int:venue_id>")
def venue_detail(venue_id):
    if not ensure_db_initialized():
        return "Database unavailable — please try again shortly.", 503
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM venues WHERE id = %s AND status = 'approved'", [venue_id])
    venue = cur.fetchone()
    if venue is None:
        return "Venue not found", 404
    return render_template("venue_detail.html", venue=venue, ratings=RATINGS)


@app.route("/submit", methods=["GET", "POST"])
@app.route("/contributor", methods=["GET", "POST"])
def submit():
    if not ensure_db_initialized():
        return "Database unavailable — please try again shortly.", 503
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
                cur = db.cursor()
                cur.execute(
                    """INSERT INTO venues
                       (venue_name, location, num_tables, price_per_game,
                        bathroom_type, rating, notes, photo_url, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')""",
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
    if not ensure_db_initialized():
        return jsonify({"error": "Database unavailable — please try again shortly."}), 503
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT rating, location, created_at, num_tables, price_per_game, bathroom_type "
        "FROM venues WHERE status = 'approved'"
    )
    venues = cur.fetchall()

    by_rating = {i: 0 for i in range(6)}
    cities = {}
    by_price = {}
    by_bathroom = {}
    year_ago = datetime.now() - timedelta(days=365)
    this_year = 0
    total_tables = 0

    for v in venues:
        by_rating[v["rating"]] = by_rating.get(v["rating"], 0) + 1
        cities[v["location"]] = cities.get(v["location"], 0) + 1
        if v["created_at"] and v["created_at"] >= year_ago:
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
    if not ensure_db_initialized():
        return "Database unavailable — please try again shortly.", 503
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM venues WHERE status = 'pending' ORDER BY created_at DESC")
    pending = cur.fetchall()
    cur.execute("SELECT * FROM venues WHERE status = 'approved' ORDER BY created_at DESC")
    approved = cur.fetchall()
    return render_template("admin.html", pending=pending, approved=approved, ratings=RATINGS)


@app.route("/admin/approve/<int:venue_id>", methods=["POST"])
@admin_required
def admin_approve(venue_id):
    if not ensure_db_initialized():
        return "Database unavailable — please try again shortly.", 503
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE venues SET status = 'approved' WHERE id = %s", [venue_id])
    db.commit()
    return redirect(url_for("admin"))


@app.route("/admin/reject/<int:venue_id>", methods=["POST"])
@admin_required
def admin_reject(venue_id):
    if not ensure_db_initialized():
        return "Database unavailable — please try again shortly.", 503
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM venues WHERE id = %s AND status = 'pending'", [venue_id])
    db.commit()
    return redirect(url_for("admin"))


@app.route("/admin/delete/<int:venue_id>", methods=["POST"])
@admin_required
def admin_delete(venue_id):
    if not ensure_db_initialized():
        return "Database unavailable — please try again shortly.", 503
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM venues WHERE id = %s", [venue_id])
    db.commit()
    return redirect(url_for("admin"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
