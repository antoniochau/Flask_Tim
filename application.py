from flask import Flask, redirect, url_for, render_template, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from blueprints.user_login import bp as user_login
from blueprints.panel import bp as panel





application = Flask ( __name__)

app = application

app.register_blueprint ( user_login , url_prefix="/user"  )
app.register_blueprint ( panel , url_prefix="/panel"  )

app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/app.db"

db = SQLAlchemy(app)
app.config['DB'] = db

class users ( db.Model ):   
    id = db.Column( "id", db.Integer, primary_key = True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    def __init__ ( self, name, email ):
        self.name = name
        self.email = email

app.config['USERS'] = users

@application.route ("/")
def home() :
    return redirect ( url_for ("user_login.index"))

if __name__ == '__main__' :
    with app.app_context():
        db.create_all()
    app.run(debug=True)
 
