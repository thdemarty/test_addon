from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from config import Config
from models import db, Event, Category, Status, Color
import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/patient')
def patient_index():
    # display events today + not all_day events
    today = datetime.datetime.now()
    start = datetime.datetime.combine(today, datetime.datetime.min.time())
    end = datetime.datetime.combine(today, datetime.datetime.max.time())
    events = Event.query.filter(
        Event.start_dt >= start,
        Event.start_dt <= end,
        Event.all_day == False
    ).order_by(Event.start_dt).all()

    context = {
        'events': events,
        'all_day_events': Event.query.filter(Event.all_day == True).all()
    }
    return render_template('index.html', **context)

@app.route('/')
def index():
    return redirect(url_for('patient_index'))


@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        all_day = request.form.get('all_day')
        
        # color is the value of a Color choice in the enum
        # 

        if all_day:
            start = datetime.datetime.fromisoformat(request.form['start_dt'])
            end_dt = start + datetime.timedelta(days=1)
        else:
            start = datetime.datetime.fromisoformat(request.form['start_dt'])
            end_dt = datetime.datetime.fromisoformat(request.form['end_dt'])

        event = Event(
            title=title,
            status=Status.PENDING,
            description=description,
            all_day=all_day is not None,
            start_dt=start,
            end_dt=end_dt,
            color=Color(request.form['color']),
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
    return render_template('events/create.html', categories=categories, statuses=Status, colors=Color)

@app.route('/categories/create', methods=['POST'])
def create_category():
    name = request.form.get('name')
    if not name:
        return "Category name is required", 400
    
    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return "Category already exists", 400
    
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()

    return {"id": category.id, "name": category.name}, 201

if __name__ == '__main__':
    app.run(debug=True)
