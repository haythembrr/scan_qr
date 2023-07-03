from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EditMachineForm, AddMachineForm
from flask import render_template, flash, redirect, url_for, request, Response, session
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Role, Machine, Document, Intervention
from werkzeug.urls import url_parse
import cv2
from datetime import datetime
from flask_socketio import SocketIO
from qr_scanner import QRScanner
import base64
import sys


socketio = SocketIO(app, cors_allowed_origins="*")
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
            with app.app_context():
                machine = Machine.query.filter_by(id=int(myData)).first()
            if machine:
                socketio.emit(
                    "scan_result",
                    {"status": "granted", "message": f"ID : {myData}", "machine_id" : myData}
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
@login_required
def video_feed():
    return Response(scan_for_qr(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/display_pdf/<file_id>')
@login_required
def display_pdf(file_id):
    file_blob = Document.query.filter_by(id=file_id).first().blob
    # Base64 encode the PDF data
    encoded_pdf = base64.b64encode(file_blob).decode('utf-8')
    # Render the PDF document template and pass the number of pages
    return render_template('display_pdf.html', encoded_pdf = encoded_pdf)


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
@login_required
def register():
    if not current_user.role == 2:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, active=form.active.data, role=form.role.data.id)
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
    return render_template('user.html', user=user)

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


@app.route('/machine/<machine_id>')
@login_required
def machine(machine_id):
    machine = Machine.query.filter_by(id=machine_id).first_or_404()
    documents = Document.query.filter_by(machine_id=machine_id)
    interventions = Intervention.query.filter_by(machine_id=machine_id)
    return render_template('machine.html', machine=machine, documents=documents, machine_id=machine_id, interventions = interventions)


@app.route('/edit_machine/<machine_id>', methods=['GET', 'POST'])
@login_required
def edit_machine(machine_id):
    machine = Machine.query.filter_by(id=machine_id).first_or_404()
    form = EditMachineForm()
    if form.validate_on_submit():
        machine.manufacturer = form.manufacturer.data
        machine.location = form.location.data
        machine.status = form.status.data
        machine.install_date = form.install_date.data
        machine.comment = form.comment.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_machine', machine_id=machine_id))
    elif request.method == 'GET':
        form.manufacturer.data = machine.manufacturer
        form.location.data = machine.location 
        form.status.data = machine.status
        form.install_date.data = machine.install_date
        form.comment.data = machine.comment
    return render_template('edit_machine.html', form=form)

@app.route('/add_machine', methods=['GET', 'POST'])
@login_required
def add_machine():
    form = AddMachineForm()
    if form.validate_on_submit():
        machine = Machine(manufacturer=form.manufacturer.data, location=form.location.data, status=form.status.data, 
                          install_date=form.install_date.data, comment =form.comment.data)
        db.session.add(machine)
        db.session.commit()
        flash('Congratulations, you added a new machine!')
    return render_template('add_machine.html', form=form)


@app.route('/add_document/<machine_id>', methods=['GET', 'POST'])
@login_required
def add_document(machine_id):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            document = Document(machine_id=machine_id, type='Plan', upload_date=datetime.utcnow(), 
                                blob=file.read(), size=sys.getsizeof(file.read()))
            db.session.add(document)
            db.session.commit()
            flash('Document added!')
            return redirect(url_for('add_document', machine_id = machine_id) )
    return render_template('add_document.html')

@app.route('/ongoing_intervention/<machine_id>', methods=['GET', 'POST'])
@login_required
def ongoing_intervention(machine_id):
    if request.method == 'POST':
        intervention = Intervention(machine_id=request.view_args.get('machine_id'), user_id=current_user.id, type="Reparation",
                                        comment = "", start_date = datetime.utcnow(), end_date = datetime.utcnow())
        db.session.add(intervention)
        db.session.commit()
        flash('Intervention ended!')
        return redirect(url_for('machine', machine_id = machine_id) )
    return render_template('intervention.html')








