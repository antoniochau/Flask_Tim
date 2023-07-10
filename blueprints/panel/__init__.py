from flask import Blueprint, render_template

bp = Blueprint('panel', __name__ )

from blueprints.panel import routes