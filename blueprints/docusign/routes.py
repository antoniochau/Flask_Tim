from blueprints.docusign import bp as docusign
from flask import Flask, render_template, session, request, flash, redirect, url_for, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from flask import current_app

from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfReader, PdfWriter

from pathlib import Path
from datetime import datetime
import time
import warnings
import glob, os, sys, shutil, io
import PIL

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont

# Registered font family
pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
# Registered fontfamily
registerFontFamily('Vera',normal='Vera',bold='VeraBd',italic='VeraIt',boldItalic='VeraBI')

# Output pdf file name.
can = canvas.Canvas("Bold_Trail.pdf", pagesize=A4)

# Setfont for whole pdf.
can.setFont('Vera', 12)



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


def makeWatermark(  inputtext ):
    
    watermarkfile = os.path.join(current_app.config['UPLOAD_FOLDER'], "watermark.pdf")
    tmp_file = Path ( watermarkfile )
    pdf = canvas.Canvas(  str( tmp_file  ), pagesize=A4)
    pdf.translate(inch, inch)
    pdf.setFillColor(colors.red, alpha=0.8)
    pdf.setFont("Times-Roman", 10)
    pdf.setFont('Vera', 12)
    pdf.rotate(20)
    pdf.rect(100, 280, 100, 100, stroke=1, fill=0) 
    pdf.drawCentredString(150, 330, f"{inputtext}"  )
    
    pdf.setFillColor(colors.black, alpha=0.8)
    pdf.setFont("Times-Roman", 7)
    
    #pdf.drawCentredString(320, 400  , f"{msg}"  )
    
    
    pdf.save()
    return ( tmp_file )

def merge_watermark_to_pdf(  form_pdf_file, watermark_pdf_file ):
    pdf_file = form_pdf_file
    
    request = pdf_file.stem
    
    watermark = watermark_pdf_file

    merged = os.path.join(current_app.config['UPLOAD_FOLDER'], request + "Watermarked.pdf")


    with open(pdf_file, "rb") as input_file, open(watermark, "rb") as watermark_file:
        input_pdf = PdfReader(input_file)
        watermark_pdf = PdfReader(watermark_file)
        watermark_page = watermark_pdf.pages[0]
        
        output = PdfWriter()
        
        for i in range( len(input_pdf.pages)):
            pdf_page = input_pdf.pages[i]
            pdf_page.merge_page(watermark_page)
            output.add_page(pdf_page)
        
    
        with open(merged, "wb") as merged_file:
            output.write(merged_file)

    return ( merged )







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
            
            signed_name = request.form['Name']

            print ( signed_name)


            filename = secure_filename(file.filename)
            newfilename = "aaa" + filename


            file_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            new_file_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], newfilename)

            file.save(file_full_path)

            pdf_file = Path ( file_full_path )
    
            watermark_pdf_file = makeWatermark (  signed_name  )
            
            new_file_full_path = merge_watermark_to_pdf(  pdf_file, watermark_pdf_file )
            new_file_full_path = Path(new_file_full_path)

            print ( "aa" , new_file_full_path.name )

            new_file_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_file_full_path.name )

            # shutil.copyfile(file_full_path, new_file_full_path)
            result = download ( new_file_full_path)
            return ( result )
            return redirect(request.url)
            



        
    return render_template ( "docusign/docusign.html")
    