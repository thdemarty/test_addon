from functools import wraps
from utils import get_user_role
from flask import request, redirect, url_for, g

def roles_required(roles: list, redirect_to=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            username = request.headers.get('X-Remote-User-Name')
            role = get_user_role(username)
            print('[DEBUG] Username:', username)
            print("[DEBUG] Role:", role)

            if role not in roles:
                if redirect_to:
                    return redirect(url_for(redirect_to))
                else:
                    return "You don't have access to the data", 403
            else:
                # Si le rôle est valide, on peut stocker le rôle dans g pour l'utiliser plus tard
                g.username = username
                g.user_role = role


            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__  # Pour éviter les soucis avec Flask
        return wrapper
    return decorator