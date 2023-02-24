from flask import Blueprint,render_template

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def hello_pybo():
    return 'okeydogie'






