import os
import sqlite3
from flask import Flask, g, redirect, render_template, request, url_for

app = Flask(__name__, static_folder=".", static_url_path="")

DATABASE = os.path.join(os.path.dirname(__file__), "pool.db")

RATINGS = {
    5: {"label": "LEGENDARY",      "stars": "🍒🍒🍒🍒🍒", "cls": "r5"},
    4: {"label": "PERFECT",    "stars": "🍒🍒🍒🍒",   "cls": "r4"},
    3: {"label": "PRETTY GOOD",  "stars": "🍒🍒🍒",     "cls": "r3"},
    2: {"label": "DECENT",       "stars": "🍒🍒",       "cls": "r2"},
    1: {"label": "OKAY",         "stars": "🍒",         "cls": "r1"},
    0: {"label": "SKIP IT",      "stars": "ㄨ",         "cls": "r0"},
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


@app.route("/pool-database")
def pool_database():
    db = get_db()
    venues = db.execute(
        "SELECT * FROM venues ORDER BY created_at DESC"
    ).fetchall()
    prices = [r[0] for r in db.execute(
        "SELECT DISTINCT price_per_game FROM venues ORDER BY price_per_game"
    ).fetchall()]
    return render_template("pool_database.html", venues=venues, ratings=RATINGS, prices=prices)


@app.route("/pool-database/<int:venue_id>")
def venue_detail(venue_id):
    db = get_db()
    venue = db.execute("SELECT * FROM venues WHERE id = ?", [venue_id]).fetchone()
    if venue is None:
        return "Venue not found", 404
    return render_template("venue_detail.html", venue=venue, ratings=RATINGS)


@app.route("/submit", methods=["GET", "POST"])
def submit():
    error = None
    if request.method == "POST":
        venue_name    = request.form.get("venue_name", "").strip()
        location      = request.form.get("location", "").strip()
        num_tables    = request.form.get("num_tables", "").strip()
        price_per_game = request.form.get("price_per_game", "").strip()
        bathroom_type = request.form.get("bathroom_type", "").strip()
        rating        = request.form.get("rating", "").strip()
        notes         = request.form.get("notes", "").strip()

        if not all([venue_name, location, num_tables, price_per_game, bathroom_type, rating]):
            error = "All fields except notes are required."
        else:
            db = get_db()
            db.execute(
                """INSERT INTO venues
                   (venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [venue_name, location, int(num_tables), price_per_game,
                 bathroom_type, int(rating), notes],
            )
            db.commit()
            return redirect(url_for("pool_database"))

    return render_template(
        "submit.html",
        error=error,
        ratings=RATINGS,
        bathroom_options=BATHROOM_OPTIONS,
    )


if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True, port=5000)
