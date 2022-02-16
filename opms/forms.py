from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask import request
from passlib.hash import pbkdf2_sha256
from opms.models import Patient, Doctor, Admin


class ForgetPassword(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})

    def validate_email(self, email):

        patient = Patient.query.filter_by(
            email=request.form.get('email')).scalar()
        doctor = Doctor.query.filter_by(
            email=request.form.get('email')).scalar()
        admin = Admin.query.filter_by(
            email=request.form.get('email')).scalar()

        print(patient)
        print(doctor)
        print(admin)

        if (patient or doctor or admin) is None:
            raise ValidationError(
                'invalid.')


class ChangePassword2(FlaskForm):

    newpassword = PasswordField('Newpassword', validators=[DataRequired()],  render_kw={
        "placeholder": "New Password"})
    confirmmpassword = PasswordField('Confirmpassword', validators=[DataRequired(), EqualTo('newpassword')],  render_kw={
        "placeholder": "Confirm Password"})


class ChangePassword(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    Oldpassword = PasswordField('Oldpassword', validators=[DataRequired()],  render_kw={
        "placeholder": "Old Password"})
    Newpassword = PasswordField('Newpassword', validators=[DataRequired()],  render_kw={
        "placeholder": "New Password"})

    def validate_Oldpassword(self, email):

        patient = Patient.query.filter_by(
            email=request.form.get('email')).scalar()
        doctor = Doctor.query.filter_by(
            email=request.form.get('email')).scalar()
        admin = Admin.query.filter_by(
            email=request.form.get('email')).scalar()
        if patient:

            if (patient.email and pbkdf2_sha256.verify(request.form.get('Oldpassword'), patient.p_hash) == False):
                raise ValidationError(
                    'Invalid')

        if doctor:

            if (doctor.email and pbkdf2_sha256.verify(request.form.get('Oldpassword'), doctor.p_hash) == False):
                raise ValidationError(
                    'Invalid')

        if admin:
            if (admin.email and pbkdf2_sha256.verify(request.form.get('Oldpassword'), admin.p_hash) == False):
                raise ValidationError(
                    'Invalid')


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={
                       "placeholder": "Name"})

    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()],  render_kw={
                             "placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confrim Password"})
    select = SelectField(choices=['patient', 'doctor', 'admin'],
                         validators=[DataRequired()])

    def validate_email(self, email):
        if(request.form.get('select') == "patient"):
            patient = Patient.query.filter_by(email=email.data).first()

            if patient:
                raise ValidationError(
                    'That email is taken. Please choose another.')
        elif (request.form.get('select') == "doctor"):
            doctor = Doctor.query.filter_by(email=email.data).first()
            if doctor:
                raise ValidationError(
                    'That email is taken. Please choose another.')
        else:
            admin = Admin.query.filter_by(email=email.data).first()
            if admin:
                raise ValidationError(
                    'That email is taken. Please choose another.')


class LoginForm(FlaskForm):

    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={
                             "placeholder": "Enter password"})

    def validate_password(self, email):

        patient = Patient.query.filter_by(
            email=request.form.get('email')).scalar()
        doctor = Doctor.query.filter_by(
            email=request.form.get('email')).scalar()
        admin = Admin.query.filter_by(
            email=request.form.get('email')).scalar()
        if patient:

            if (patient.email and pbkdf2_sha256.verify(request.form.get('password'), patient.p_hash) == False):
                raise ValidationError(
                    'Invalid')

        if doctor:

            if (doctor.email and pbkdf2_sha256.verify(request.form.get('password'), doctor.p_hash) == False):
                raise ValidationError(
                    'Invalid')

        if admin:
            if (admin.email and pbkdf2_sha256.verify(request.form.get('password'), admin.p_hash) == False):
                raise ValidationError(
                    'Invalid')
