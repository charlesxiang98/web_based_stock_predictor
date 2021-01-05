from functools import wraps

from flask import request, current_app


def jsonp(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('jsonp_callback', False)
        if callback:
            content = str(callback) + '(' + func(*args, **kwargs).data.decode() + ')'
            return current_app.response_class(content, mimetype='application/javascript')
        else:
            return func(*args, **kwargs)

    return decorated_function
