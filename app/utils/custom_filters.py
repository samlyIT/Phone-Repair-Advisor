import json

def from_json(value):
    """
    A Jinja2 filter to parse a JSON string into a Python object.
    """
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None

def register_filters(app):
    """
    Register custom Jinja2 filters with the Flask app.
    """
    app.jinja_env.filters['from_json'] = from_json
