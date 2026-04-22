# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bar(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    city          = db.Column(db.String(100), nullable=False)   # "Portland, OR"
    tables        = db.Column(db.Integer, nullable=False)       # number of pool tables
    cost_per_game = db.Column(db.Float, nullable=False)         # e.g. 0.50
    bathrooms     = db.Column(db.String(50))                    # "Gendered", "All-Gender", etc.
    rating        = db.Column(db.Integer, nullable=False)       # 1–5 stars
    has_atm       = db.Column(db.Boolean, default=False)
    has_chalk     = db.Column(db.Boolean, default=True)
    good_lighting = db.Column(db.Boolean, default=False)
    level_table   = db.Column(db.Boolean, default=False)
    notes         = db.Column(db.Text)
    photo         = db.Column(db.String(200))                   # filename in /static/uploads/