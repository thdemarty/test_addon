from flask import Flask, request
from flask import render_template
from utils import get_user_role

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stderr',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)


app.config.from_prefixed_env()


@app.route("/")
def hello_world():
    if not app.config["core_addon_hostname"] or app.config["core_addon_hostname"] == "":
        return render_template("missconfig.html")


    username = request.headers.get("X-Remote-User-Name")
    context = {
        "username": username,
        "role": get_user_role(username.strip()),
    }
    return render_template("index.html", **context)
