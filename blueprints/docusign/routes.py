from blueprints.docusign import bp as docusign
from flask import Flask, render_template, session, request, flash, redirect, url_for, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import os, shutil
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfFileReader, PdfFileWriter


ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def download(path):
    #print ( os.path.abspath(current_app.config['UPLOAD_FOLDER']) )
    #return send_from_directory( os.path.abspath(current_app.config['UPLOAD_FOLDER']), filename, as_attachment=True)
    print ( path)
    return send_file(path, as_attachment=True)

    #return send_from_directory( os.path.abspath(current_app.config['UPLOAD_FOLDER']), filename)



@docusign.route('/index' , methods=['GET', 'POST']) 
@docusign.route('/' , methods=['GET', 'POST']) 
def index():
    print ( "fdf")
    if "access_right" not in session :
        return redirect ( url_for("user_login.index"))


 
    if request.method == 'POST':
        # check if the post request has the file part
        print ( request.files['file'])
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        print ("fdfdaaa")   
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            

            print ( file)
            filename = secure_filename(file.filename)
            newfilename = "aaa" + filename
            absolute_path = os.path.abspath(current_app.config['UPLOAD_FOLDER']+filename)
            print ( absolute_path)

            file_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            new_file_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], newfilename)

            file.save(file_full_path)

            shutil.copyfile(file_full_path, new_file_full_path)
            result = download ( new_file_full_path)
            return ( result )
            return redirect(request.url)
            



        
    return render_template ( "docusign/docusign.html")
    