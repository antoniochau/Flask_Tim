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
import textwrap
import qrcode

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



def qr_makeWatermark(  inputtext ):
    
    img = qrcode.make( inputtext )
    # Saving as an image file
    QRcode_file = os.path.join(current_app.config['UPLOAD_FOLDER'], "qrcode.png" )
    img.save( QRcode_file )

    watermarkfile = os.path.join(current_app.config['UPLOAD_FOLDER'], "qr_watermark.pdf")
    tmp_file = Path ( watermarkfile )
    pdf = canvas.Canvas(  str( tmp_file  ), pagesize=A4)
   

    x_start = 50
    y_start = 600
    pdf.drawImage(QRcode_file, x_start, y_start, width=50, preserveAspectRatio=True, mask='auto')
    pdf.setFillColor(colors.red, alpha=0.5)
    pdf.showPage()
    
    pdf.save()
    
    
    return ( tmp_file )

def makeWatermark(  inputtext ):
    
    watermarkfile = os.path.join(current_app.config['UPLOAD_FOLDER'], "watermark.pdf")
    tmp_file = Path ( watermarkfile )
    pdf = canvas.Canvas(  str( tmp_file  ), pagesize=A4)
    pdf.translate(inch, inch)
    pdf.setFillColor(colors.red, alpha=0.8)
    pdf.setFont("Times-Roman", 10)
    pdf.setFont('Vera', 12)
    pdf.rotate(20)
    #pdf.rect(100, 280, 100, 100, stroke=1, fill=0) 
    pdf.circle(150, 330, 60, stroke=1, fill=0) 

    wrapper = textwrap.TextWrapper(width=15)
    word_list = wrapper.wrap(text = inputtext )
    

    y = 330
    for element in word_list:
        pdf.drawCentredString(150, y, element  )
        y -= 15

    pdf.setFillColor(colors.black, alpha=0.8)
    pdf.setFont("Times-Roman", 7)    
    pdf.save()
    return ( tmp_file )

def merge_watermark_to_pdf(  form_pdf_file, watermark_pdf_file ):
    pdf_file = form_pdf_file
    
    request = pdf_file.stem
    
    watermark = watermark_pdf_file

    merged = os.path.join(current_app.config['UPLOAD_FOLDER'], request + "_Signed.pdf")

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
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            
            signed_name = request.form['Name']

            filename = secure_filename(file.filename)
            #signed_filename =  filename + "_signed"

            input_file = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            #output_file = os.path.join(current_app.config['UPLOAD_FOLDER'], signed_filename )

            file.save(input_file)

            input_file_path = Path ( input_file )
    
            watermark_pdf_file = makeWatermark (  signed_name  )
            
            output_file = merge_watermark_to_pdf(  input_file_path , watermark_pdf_file )
            output_file_path = Path( output_file )

   

            output_file_path_str = os.path.join(current_app.config['UPLOAD_FOLDER'], output_file_path.name )

            # shutil.copyfile(file_full_path, new_file_full_path)
            result = download ( output_file_path_str )
            return ( result )
            return redirect(request.url)
            
    
    return render_template ( "docusign/docusign.html")
    


@docusign.route('/QR' , methods=['GET', 'POST']) 
def QRindex():
    
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
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            
            signed_name = request.form['Name']

            filename = secure_filename(file.filename)
            #signed_filename =  filename + "_signed"

            input_file = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            #output_file = os.path.join(current_app.config['UPLOAD_FOLDER'], signed_filename )

            file.save(input_file)

            input_file_path = Path ( input_file )
    
            qr_watermark_pdf_file = qr_makeWatermark (  signed_name  )
            
            output_file = merge_watermark_to_pdf(  input_file_path , qr_watermark_pdf_file )
            output_file_path = Path( output_file )

   

            output_file_path_str = os.path.join(current_app.config['UPLOAD_FOLDER'], output_file_path.name )

            # shutil.copyfile(file_full_path, new_file_full_path)
            result = download ( output_file_path_str )
            return ( result )
            return redirect(request.url)
            
    
    return render_template ( "docusign/QRdocusign.html")
    