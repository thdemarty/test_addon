from flask import Flask, request
from flask import render_template
from utils import get_user_role


app = Flask(__name__)
app.config.from_prefixed_env()

@app.route("/")
def home():
    if not app.config["core_addon_hostname"] or app.config["core_addon_hostname"] == "":
        return render_template("missconfig.html")

    username = request.headers.get("X-Remote-User-Name")
    if app.config['DEBUG']:
        username = "admin"
    context = {
        "username": username,
        "role": get_user_role(username.strip()),
    }
    return render_template("index.html", **context)



