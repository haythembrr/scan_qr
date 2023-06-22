from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask import render_template, flash, redirect, url_for, request, Response
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
import cv2
from PyPDF2 import PdfFileReader
import os
from datetime import datetime
from flask_socketio import SocketIO, emit
from qr_scanner import QRScanner
import time

socketio = SocketIO(app, cors_allowed_origins="*")
myDataDB = ["1", "2"]
qr_code_scanner = QRScanner()


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

def scan_for_qr():
    camera = cv2.VideoCapture(0)
    while True:
        is_granted, is_denied = False, False
        success, image = camera.read()
        if not success:
            break
        
        result = QRScanner.read_qr_code(image)

        if len(result) == 0:
           socketio.emit(
                "scan_result",
                {"status": "scan", "message": "Please scan your QR Code"},
            )

        for barcode in result:
            myData = barcode.data.decode("utf-8")
            if myData in myDataDB:
                socketio.emit(
                    "scan_result",
                    {"status": "granted", "message": f"ID : {myData}", "file_id" : myData}
                )
                is_granted = True
            else:
                print("Not found in the database!")
                socketio.emit(
                    "scan_result", {"status": "denied", "message": f"ID : {myData}"}
                )
                is_denied = True
            QRScanner.add_box_to_qr_code(image, barcode)

        if is_granted:
            image = qr_code_scanner.get_access_granted_img()
        elif is_denied:
            image = qr_code_scanner.get_access_denied_img()
                
        frame = QRScanner.encode(image)

        if is_granted or is_denied:
            for _ in range(2):
                yield (b"--frame\r\n" + b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        else:
            yield (b"--frame\r\n" + b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
    

@app.route('/video_feed')
def video_feed():
    return Response(scan_for_qr(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/display_pdf/<file_id>')
def display_pdf(file_id):
    pdf = PdfFileReader(open('app/static/plans/' + file_id + '.pdf', 'rb'))
    num_pages = pdf.getNumPages()


    # Render the PDF document template and pass the number of pages
    return render_template('display_pdf.html', num_pages=num_pages, file_id=file_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)