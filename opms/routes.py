from sqlalchemy.orm.query import AliasOption
from opms import app, s, db, mail
from opms.forms import RegistrationForm, LoginForm, ChangePassword, ForgetPassword, ChangePassword2
from opms.models import Patient, Doctor, Admin, Medical_Specialty, Doctor_Schedule, Patient_Schedule
from flask import render_template, flash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import render_template, request,  redirect, url_for, flash
from passlib.hash import pbkdf2_sha256
from flask_mail import Mail, Message
from wtforms.validators import ValidationError
from flask_login import login_user, current_user, logout_user, login_required


@ app.route('/')
def home():
    return render_template('index.html')


@ app.route('/signup', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():

        hashed_password = pbkdf2_sha256.encrypt(form.password.data)
        if(request.form.get('select') == "patient"):
            patient = Patient(name=form.name.data,
                              email=form.email.data, p_hash=hashed_password, role=form.select.data, actual_role="patient", confirmed=False)
            db.session.add(patient)
            db.session.commit()
        elif(request.form.get('select') == "doctor"):

            doctor = Doctor(name=form.name.data,
                            email=form.email.data, p_hash=hashed_password, role=form.select.data, price=0.00, actual_role="patient", confirmed=False)
            db.session.add(doctor)
            db.session.commit()
        else:

            admin = Admin(name=form.name.data,
                          email=form.email.data, p_hash=hashed_password, role=form.select.data, actual_role="patient", confirmed=False)
            db.session.add(admin)
            db.session.commit()
        print(request.form)
        email = form.email.data
        token = s.dumps(email, salt='email-confirm')

        msg = Message('Confirm Email',
                      sender='faresahmed91920@gmail.com', recipients=[email])

        link = url_for('confirm_email', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)
        return render_template('confirmation.html')

    return render_template('signup.html', form=form)


@ app.route('/confirm_email/<token>')
def confirm_email(token):

    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        print(email)

        patient = Patient.query.filter_by(
            email=email).scalar()
        if patient:
            patient.confirmed = True
            db.session.commit()
        doctor = Doctor.query.filter_by(
            email=email).scalar()
        if doctor:
            doctor.confirmed = True
            db.session.commit()
        admin = Admin.query.filter_by(
            email=email).scalar()
        if admin:
            admin.confirmed = True
            db.session.commit()

    except SignatureExpired:
        return render_template('token_expired.html')
    return render_template('registered.html')


@ app.route('/patient')
@login_required
def patient():
    patient = Patient.query.filter_by(id=current_user.id).first()
    print(patient.name)
    return render_template('patient.html')


@ app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        patient = Patient.query.filter_by(email=form.email.data).first()
        doctor = Doctor.query.filter_by(email=form.email.data).first()
        admin = Admin.query.filter_by(email=form.email.data).first()
        if patient:

            if (patient.actual_role == "patient"):
                login_user(patient)
                return redirect(url_for('patient'))
        if doctor:
            if (doctor.actual_role == "doctor"):
                login_user(doctor)
                return redirect(url_for('doctor'))

        if admin:

            if (admin.actual_role == "admin"):
                login_user(admin)
                return redirect(url_for('admin.index'))

    return render_template('login.html', form=form)


@ app.route('/doctor')
@login_required
def doctor():
    doctor = Doctor.query.filter_by(id=current_user.id).first()
    print(doctor.name)
    return render_template('doctor.html')


@ app.route('/my-profile-doctor', methods=['GET', 'POST'])
def doctor_profile():
    doctor = Doctor.query.filter_by(id=current_user.id).first()
    if request.method == 'POST':
        Name = request.form.get("name")
        phone_no = request.form.get("phone")
        doctor.name = Name
        doctor.phone_no = phone_no
        db.session.commit()
        print(request.form.get("name"))

    return render_template('my-profile-doctor.html', doctor=doctor)


@ app.route('/add-my-schedule', methods=['GET', 'POST'])
def add_my_schedual():
    doctor = Doctor.query.filter_by(id=current_user.id).first()
    if request.method == 'POST':
        rep = request.form.get("rep")
        day = request.form.get("day")
        month = request.form.get("month")
        fromti = request.form.get("fromti")
        totime = request.form.get("totime")
        print(rep)
        print(day)
        print(month)
        print(fromti)
        print(totime)
        print(doctor.schedule)
        if(rep == '0' or day == '0' or fromti == '' or totime == ''):
            return render_template('add-my-schedule.html', doctor=doctor)
        elif(rep == 'Every'):

            dosc = doctor.schedule.filter_by(repetition=rep,
                                             day=day, month=None, from_time=fromti, to_time=totime).first()
            if dosc:
                return render_template('add-my-schedule.html', doctor=doctor)

            d_s = Doctor_Schedule(repetition=rep,
                                  day=day, month=None, from_time=fromti, to_time=totime, room_no=None)
            db.session.add(d_s)
            doctor.schedule.append(d_s)
            db.session.commit()
        elif(month == ''):
            return render_template('add-my-schedule.html', doctor=doctor)

        else:

            dosc = doctor.schedule.filter_by(repetition=rep,
                                             day=day, month=month, from_time=fromti, to_time=totime).first()
            if dosc:
                return render_template('add-my-schedule.html', doctor=doctor)
            d_s = Doctor_Schedule(repetition=rep,
                                  day=day, month=month, from_time=fromti, to_time=totime, room_no=None,)
            db.session.add(d_s)
            doctor.schedule.append(d_s)
            db.session.commit()
    return render_template('add-my-schedule.html', doctor=doctor)


@ app.route('/my-schedual')
def my_schedual():

    doctor = Doctor.query.filter_by(id=current_user.id).first()

    return render_template('my-schedual.html', doctor=doctor)


@ app.route('/Confirmed-Email')
def Confirm_email():
    return render_template('Confirmed-Email.html')


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    form = ChangePassword()

    if form.validate_on_submit():

        em = form.email.data
        opw = form.Oldpassword.data
        npw = form.Newpassword.data

        patient = Patient.query.filter_by(email=form.email.data).first()
        doctor = Doctor.query.filter_by(email=form.email.data).first()
        admin = Admin.query.filter_by(email=form.email.data).first()

        if patient:

            hashed_password = pbkdf2_sha256.encrypt(npw)
            patient.p_hash = hashed_password
            db.session.commit()

            return redirect(url_for('logout'))

        if doctor:

            hashed_password = pbkdf2_sha256.encrypt(npw)
            doctor.p_hash = hashed_password
            db.session.commit()

            return redirect(url_for('logout'))

        if admin:

            hashed_password = pbkdf2_sha256.encrypt(npw)
            admin.p_hash = hashed_password
            db.session.commit()

            return redirect(url_for('logout'))
    return render_template('change-password.html', form=form)


@ app.route('/my-profile-patient', methods=['GET', 'POST'])
def patient_profile():
    patient = Patient.query.filter_by(id=current_user.id).first()
    print(current_user.id)
    if request.method == 'POST':
        Name = request.form.get("name")
        print(Name)
        phone_no = request.form.get("phone")
        patient.name = Name
        patient.phone_no = phone_no
        db.session.commit()
        print(request.form.get("name"))
    return render_template('my-profile-patient.html', patient=patient)


@ app.route('/book-appointment', methods=['GET', 'POST'])
def book():
    patient = Patient.query.filter_by(id=current_user.id).first()

    specialty = Medical_Specialty.query.all()
    doctor = Doctor.query.all()
    ds = Doctor_Schedule.query.all()
    if request.method == 'POST':

        sp = request.form.get("sp")

        d = request.form.get("doc")
        print(sp)
        print(d)

        if(sp != 'medical specialties'):
            doc = Doctor.query.filter(
                Doctor.specialty.has(specialties=sp)).all()

            name = request.form.get("name")

            spec = request.form.get("specialty")

            price = request.form.get("price")

            day1 = request.form.get("day")

            date1 = request.form.get("date")

            fromt1 = request.form.get("fromt")

            to1 = request.form.get("to")

            room1 = request.form.get("room")
            if(name != None):
                print(name)
                print(spec)
                print(price)
                print(day1)
                print(date1)

                print(fromt1)
                print(to1)
                print(room1)
                if (date1 == "None"):
                    date1 = None
                if (room1 == "None"):
                    room1 = None

                psc = patient.schedule.filter_by(
                    doctor_name=name, MedicalSpecialtiy=spec, day=day1, month=date1, from_time=fromt1, to_time=to1).first()
                if psc:
                    return render_template('book-appointment.html', patient=patient, specialty=specialty, doctor=doctor, ds=ds, doc=doc)

                print("test")
                ps = Patient_Schedule(patient_name=patient.name, doctor_name=name, MedicalSpecialtiy=spec,
                                      day=day1, month=date1, from_time=fromt1, to_time=to1, price=price, room_no=room1)
                db.session.add(ps)
                patient.schedule.append(ps)
                db.session.commit()

            return render_template('book-appointment.html', patient=patient, specialty=specialty, doctor=doctor, ds=ds, doc=doc)
        if(d != 'Doctor'):
            print(d)
            #do = d[1:-1]
            # print(do)

            doc = Doctor.query.filter_by(name=d).all()
            name = request.form.get("name")

            spec = request.form.get("specialty")

            price = request.form.get("price")

            day1 = request.form.get("day")

            date1 = request.form.get("date")

            fromt1 = request.form.get("fromt")

            to1 = request.form.get("to")

            room1 = request.form.get("room")

            if(name != None):
                print(name)
                print(spec)
                print(price)
                print(day1)
                print(date1)

                print(fromt1)
                print(to1)
                print(room1)
                if (date1 == "None"):
                    date1 = None
                if (room1 == "None"):
                    room1 = None

                psc = patient.schedule.filter_by(
                    doctor_name=name, MedicalSpecialtiy=spec, day=day1, month=date1, from_time=fromt1, to_time=to1).first()
                if psc:
                    return render_template('book-appointment.html', patient=patient, specialty=specialty, doctor=doctor, ds=ds, doc=doc)
                ps = Patient_Schedule(patient_name=patient.name, doctor_name=name, MedicalSpecialtiy=spec,
                                      day=day1, month=date1, from_time=fromt1, to_time=to1, price=price, room_no=room1)
                db.session.add(ps)
                patient.schedule.append(ps)
                db.session.commit()

            return render_template('book-appointment.html', patient=patient, specialty=specialty, doctor=doctor, ds=ds, doc=doc)

    return render_template('book-appointment.html', patient=patient, specialty=specialty, doctor=doctor, ds=ds)


@ app.route('/my-appointment')
def my_appointment():

    ps = Patient.query.filter_by(id=current_user.id).first()

    return render_template('my-appointment.html', ps=ps)


@ app.route('/received-services')
def received_services():
    ps = Patient.query.filter_by(id=current_user.id).first()
    return render_template('received-services.html', ps=ps)


@ app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@ app.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    form = ForgetPassword()

    if form.validate_on_submit():
        email = form.email.data
        token = s.dumps(email, salt='reset-password')

        msg = Message('reset password',
                      sender='faresahmed91920@gmail.com', recipients=[email])

        link = url_for('reset_password', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)
        return render_template('reset.html')

    return render_template('forget-password.html', form=form)


@ app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    form = ChangePassword2()
    
    try:
            
            email = s.loads(token, salt='reset-password', max_age=3600)
            if form.validate_on_submit():
                hashed_password = pbkdf2_sha256.encrypt(form.newpassword.data)

                patient = Patient.query.filter_by(
                    email=email).scalar()
                if patient:
                    patient.p_hash = hashed_password
                    db.session.commit()
                doctor = Doctor.query.filter_by(
                    email=email).scalar()
                if doctor:
                    doctor.p_hash = hashed_password
                    db.session.commit()
                admin = Admin.query.filter_by(
                    email=email).scalar()
                if admin:
                    admin.p_hash = hashed_password
                    db.session.commit()
                return redirect(url_for('login'))
            
    except SignatureExpired:
        return render_template('token-expired.html')
    return render_template('reset-password.html', form=form)
