from utils import get_user_role, redirect
from flask import request, g
import logging 

def roles_required(roles: list, redirect_to=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            username = request.headers.get('X-Remote-User-Name')
            role = get_user_role(username)
            logging.debug(f"Username: {username}, Role: {role}")

            if role not in roles:

                return redirect('/')
            else:
                # Si le rôle est valide, on peut stocker le rôle dans g pour l'utiliser plus tard
                g.username = username
                g.user_role = role


            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__  # Pour éviter les soucis avec Flask
        return wrapper
    return decorator