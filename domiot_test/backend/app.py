from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from config import Config
from models import db, Event, Category, Status
import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/patient')
def patient_index():
    events = Event.query.order_by(Event.start_dt).all()
    return render_template('index.html', events=events)

@app.route('/')
def index():
    return redirect(url_for('patient_index'))


@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        start_dt = datetime.datetime.fromisoformat(request.form['start_dt'])
        end_dt = datetime.datetime.fromisoformat(request.form['end_dt'])

        event = Event(
            title=title,
            status=Status.PENDING,
            description=description,
            start_dt=start_dt,
            end_dt=end_dt
        )

        selected_category_ids = request.form.getlist('categories')
        for cid in selected_category_ids:
            category = Category.query.get(int(cid))
            if category:
                event.categories.append(category)

        db.session.add(event)
        db.session.commit()
        return redirect(url_for('patient_index'))

    categories = Category.query.order_by(Category.name).all()
    return render_template('events/create.html', categories=categories, statuses=Status)


if __name__ == '__main__':
    app.run(debug=True)
