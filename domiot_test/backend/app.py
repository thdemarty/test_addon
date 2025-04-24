from flask import Flask, render_template, request
from flask_migrate import Migrate
from config import Config
from models import db, Event, Category, Status, Color, Role
from utils import get_user_role, redirect, url_for
from decorators import roles_required
import datetime
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

@app.context_processor
def inject_url_for():
    """
    Inject the `url_for` function into the template context. This allows us to 
    use the `url_for` function in the templates.
    """
    return dict(url_for=url_for)


@app.route('/healthcare_staff')
@roles_required(["healthcare_staff"], redirect_to='index')
def healthcare_staff_index():
    events = Event.query.all()

    context = {
        'events': events,
    }

    return render_template('healthcare_index.html', **context)

@app.route('/patient')
@roles_required(["patient"], redirect_to='index')
def patient_index():
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
    ingress_path = request.headers.get('X-Ingress-Path', '')

    username = request.headers.get('X-Remote-User-Name')
    role = get_user_role(username)

    logging.debug(f"Username: {username}, Role: {role}")

    if not app.debug and 'CORE_ADDON_HOSTNAME' and app.config['CORE_ADDON_HOSTNAME'] == "" not in app.config:
        return redirect('missconfig')

    if role == 'patient':
        return redirect("/patient")
    elif role == 'healthcare_staff':
        return redirect("/healthcare_staff")
    elif role == 'technician':
        return "You don't have access to the data", 200
    else:
        return "No role found", 500
    

@app.route('/missconfig')
def missconfig():
    return render_template('missconfig.html')

@app.route('/add', methods=['GET', 'POST'])
@roles_required(["healthcare_staff"], redirect_to='index')
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        all_day = request.form.get('all_day')

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

        return redirect("patient")

    categories = Category.query.order_by(Category.name).all()
    return render_template('events/create.html', categories=categories, statuses=Status, colors=Color)

@app.route('/categories/create', methods=['POST'])
@roles_required(["healthcare_staff"], redirect_to='index')
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
