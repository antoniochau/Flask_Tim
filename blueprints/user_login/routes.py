from blueprints.user_login import bp as user_login
from flask import Flask, render_template, session, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import qrcode




@user_login.route('/index')
@user_login.route('/')
def index():
    return render_template ( "user_login/login.html")


@user_login.route ("/view/")
def view() :
    users = current_app.config["USERS"]
    return render_template ( "user_login/view.html", values = users.query.all() )


@user_login.route ("/login", methods=['POST','GET'])
def login() :

    users = current_app.config["USERS"]
    db = current_app.config["DB"]

    if request.method == 'POST':
        access_code = request.form['access_code']
        
        
        #session['user'] = user

        #found_user = users.query.filter_by(name=user).first()

        if access_code == "0920":
            #session['email'] = found_user.email
            session['access_right'] = True
            flash ( "login success")
            return redirect ( url_for("panel.index"))
        else:
            print ( "fdsfds")
            #usr = users ( user, "")
            #db.session.add ( usr )
            #db.session.commit()
            return redirect ( url_for("user_login.index"))
        
    else:
        print ("fdsf")
        if "access_right" in session:
            flash ("already login")
            print ( "lll")
            return redirect ( url_for ("panel.index"))
        print ( "ddd")
        return render_template ("user_login/login.html")
    
@user_login.route ("/user", methods=['POST','GET'])
def user() :

    users = current_app.config["USERS"]
    db = current_app.config["DB"]
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
        

        return render_template( "user_login/user.html", email=email , user=user)
    else:
        flash ( "You are not login")
        return redirect ( url_for ("user_login.login"))