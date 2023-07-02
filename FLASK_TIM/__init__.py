from flask import Blueprint, render_template

bp = Blueprint('user_login', __name__ )

from blueprints.user_login import routes