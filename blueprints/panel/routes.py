from blueprints.panel import bp as panel
from flask import Flask, render_template, session, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import current_app



@panel.route('/index')
@panel.route('/')
def index():
    if "access_right" in session :
        print ( "good")
        return render_template ( "panel/main_panel.html")
    else:
        return redirect ( url_for("user_login.index"))


