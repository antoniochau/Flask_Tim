from flask import Flask, redirect, url_for, render_template, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from blueprints.user_login import user_login


app = Flask ( __name__)
app.register_blueprint ( user_login, url_prefix="/test")


app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/app.db"
db = SQLAlchemy(app)

class users ( db.Model ):   
    id = db.Column( "id", db.Integer, primary_key = True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    def __init__ ( self, name, email ):
        self.name = name
        self.email = email









@app.route ("/")
def home() :
    return redirect ( url_for ("user"))

@app.route ("/user", methods=['POST','GET'])
def user() :
    email = None
    if "user" in session :
        user = session['user']
        
        if request.method == 'POST':
            email = request.form['email']
            session['email'] = email
            found_user = users.query.filter_by(name = user).first()
            found_user.email = email
            db.session.commit()
            flash ( "email was saved")
        else:
            if 'email' in session:
                email = session ['email']
        

        return render_template( "user.html", email=email , user=user)
    else:
        flash ( "You are not login")
        return redirect ( url_for ("login"))

@app.route ("/login", methods=['POST','GET'])
def login() :
    if request.method == 'POST':
        user = request.form['nm']
        session['user'] = user

        found_user = users.query.filter_by(name=user).first()

        if found_user:
            session['email'] = found_user.email

        else:
            usr = users ( user, "")
            db.session.add ( usr )
            db.session.commit()


        flash ("login success")
        return redirect ( url_for("user"))
    else:
        if "user" in session:
            flash ("already login")
            return redirect ( url_for ("user"))
        return render_template ("login.html")
    

@app.route ("/logout")
def logout() :
    session.pop("user",None)
    session.pop("email",None)

    return redirect ( url_for ("login"))

@app.route ("/view/")
def view() :
    return render_template ( "view.html", values = users.query.all() )

if __name__ == '__main__' :
    with app.app_context():
        db.create_all()
    app.run(debug=True)
 
