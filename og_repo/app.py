import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from models import db, Bar

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bars.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

db.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def create_tables():
    db.create_all()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    bars = Bar.query.order_by(Bar.rating.desc()).all()
    return render_template('index.html', bars=bars)

@app.route('/bar/<int:bar_id>')
def bar_detail(bar_id):
    bar = Bar.query.get_or_404(bar_id)
    return render_template('bar.html', bar=bar)

@app.route('/add', methods=['GET', 'POST'])
def add_bar():
    if request.method == 'POST':
        photo_filename = None
        file = request.files.get('photo')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_filename = filename

        bar = Bar(
            name          = request.form['name'],
            city          = request.form['city'],
            tables        = int(request.form['tables']),
            cost_per_game = float(request.form['cost_per_game']),
            bathrooms     = request.form['bathrooms'],
            rating        = int(request.form['rating']),
            has_atm       = 'has_atm' in request.form,
            has_chalk     = 'has_chalk' in request.form,
            good_lighting = 'good_lighting' in request.form,
            level_table   = 'level_table' in request.form,
            notes         = request.form.get('notes', ''),
            photo         = photo_filename,
        )
        db.session.add(bar)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_bar.html')

if __name__ == '__main__':
    app.run(debug=True)