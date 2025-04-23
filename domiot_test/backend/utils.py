import json
from urllib import request
from flask import current_app as app

def get_user_role(username=""):
    app.config.from_prefixed_env()

    core_addon = app.config.get("core_addon_hostname")
    api_url = f"http://{core_addon}:8099/api/users/{username}"
    print("API URL: ", api_url)
    if not app.config["DEBUG"]:
        with request.urlopen(api_url) as response:
            data = response.read()
            print("Response: ", data)
            # Decode bytes to string
            data = data.decode("utf-8")
            # Convert JSON string to Python dictionary
            data = json.loads(data)

            return data["domiot_role"]
    else:
        # Simulate a response for testing purposes
        return "patient"


            