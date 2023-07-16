from blueprints.docusign import bp as docusign
from flask import Flask, render_template, session, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import current_app



@docusign.route('/index')
@docusign.route('/')
def index():
    if "access_right" in session :
        print ( "good")
        return render_template ( "docusign/docusign.html")
    else:
        return redirect ( url_for("docusign.index"))


