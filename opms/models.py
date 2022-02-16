
from sqlalchemy.orm import backref
from sqlalchemy_utils import ChoiceType
from opms import login_manager, admin, db
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView
from flask_login import UserMixin, current_user
from flask import url_for
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):

    patient = Patient.query.filter_by(id=user_id).first()
    doctor = Doctor.query.filter_by(id=user_id).first()
    admin = Admin.query.filter_by(id=user_id).first()
    if patient:
        return (patient)
    if doctor:
        return(doctor)
    if admin:
        return(admin)


roles = [(u'admin', u'Admin'), (u'patient',
                                u'Patient'), (u'doctor', u'Doctor')]

association_table = db.Table('association',
                             db.Column('Patient_id', db.Integer,
                                       db.ForeignKey('Patient.id')),
                             db.Column('Patient_Schedule_id', db.Integer,
                                       db.ForeignKey('Patient_Schedule.id'))
                             )

association_table2 = db.Table('association2',
                              db.Column('Doctor_id', db.Integer,
                                        db.ForeignKey('Doctor.id')),
                              db.Column('Doctor_Schedule_id', db.Integer,
                                        db.ForeignKey('Doctor_Schedule.id'))
                              )

association_table3 = db.Table('association3',
                              db.Column('Patient_id', db.Integer,
                                        db.ForeignKey('Patient.id')),
                              db.Column('Services_id', db.Integer,
                                        db.ForeignKey('Services.id'))
                              )


class Patient(db.Model, UserMixin):
    __tablename__ = 'Patient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone_no = db.Column(db.String())
    p_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    actual_role = db.Column(ChoiceType(roles), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    schedule = db.relationship("Patient_Schedule", secondary=association_table,
                               backref=db.backref('patient'), lazy='dynamic')
    services = db.relationship(
        "Services", secondary=association_table3, backref=db.backref('patient'), lazy='dynamic')

    def __repr__(self):
        return (self.name)


class MedicalView(ModelView):
    form_columns = ['specialties', 'doctor']


class Medical_Specialty(db.Model):
    __tablename__ = 'Medical_Specialty'
    id = db.Column(db.Integer, primary_key=True)
    specialties = db.Column(db.String, nullable=False)

    doctor = db.relationship("Doctor", back_populates="specialty",
                             lazy=True)

    def __repr__(self):
        return '{}'.format(self.specialties)


class Doctor(db.Model, UserMixin):
    __tablename__ = 'Doctor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone_no = db.Column(db.String())
    price = db.Column(db.Float())

    p_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    actual_role = db.Column(ChoiceType(roles), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    medical_specialty_id = db.Column(
        db.Integer, db.ForeignKey('Medical_Specialty.id'))

    specialty = db.relationship(
        "Medical_Specialty", back_populates="doctor", foreign_keys=[medical_specialty_id], lazy=True)

    schedule = db.relationship(
        "Doctor_Schedule", secondary=association_table2, backref=db.backref('doctor'), lazy='dynamic')

    def __repr__(self):
        return (self.name)


class Doctor_Schedule(db.Model):
    __tablename__ = 'Doctor_Schedule'
    id = db.Column(db.Integer, primary_key=True)
    repetition = db.Column(db.String)
    day = db.Column(db.String)
    month = db.Column(db.Date)
    from_time = db.Column(db.Time)
    to_time = db.Column(db.Time)
    room_no = db.Column(db.Integer)

    def __repr__(self):
        return '{} {} {} {} '.format(self.day, self.month, self.from_time, self.to_time)


class Patient_Schedule(db.Model):
    __tablename__ = 'Patient_Schedule'
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String)
    doctor_name = db.Column(db.String)
    MedicalSpecialtiy = db.Column(db.String)
    day = db.Column(db.String)
    month = db.Column(db.Date)
    from_time = db.Column(db.Time)
    to_time = db.Column(db.Time)
    price = db.Column(db.Float)
    room_no = db.Column(db.Integer)

    def __repr__(self):
        return '{} {} {} {} {} {} {} {} '.format(self.doctor_name, self.MedicalSpecialtiy, self.day, self.month, self.from_time, self.to_time, self.price, self.room_no)


class ScheduleView(ModelView):
    form_columns = ['repetition', 'day', 'month',
                    'from_time', 'to_time', 'room_no']
    column_exclude_list = ('Doctor')


class PScheduleView(ModelView):
    form_columns = ['patient_name', 'doctor_name', 'MedicalSpecialtiy', 'price', 'day', 'month',
                    'from_time', 'to_time', 'room_no']
    column_exclude_list = ('Patient')


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    p_hash = db.Column(db.String, nullable=False)
    phone_no = db.Column(db.String(11))
    role = db.Column(db.String, nullable=False)
    actual_role = db.Column(ChoiceType(roles), nullable=False)

    confirmed = db.Column(db.Boolean, nullable=False)


def mydefault(context):
    price = context.get_current_parameters()['Service_price']
    discount = context.get_current_parameters()['discount']
    cal = (price/100)*discount
    total = price-cal

    return total


class Services(db.Model):
    __tablename__ = 'Services'
    id = db.Column(db.Integer, primary_key=True)
    Service_name = db.Column(db.String, nullable=False)
    Service_price = db.Column(db.Float, nullable=False, default=0)
    discount = db.Column(db.Float, default=0)

    # def Total(self):
    # return ((self.price-self.discount)

    total = db.Column(db.Float, default=mydefault)

    def __repr__(self):
        return '{} {} {}  '.format(self.Service_name, self.Service_price, self.discount)


class ServicesView(ModelView):
    form_columns = ['Service_name', 'Service_price', 'discount']
    column_exclude_list = ('Patient')


class PatientView(ModelView):
    form_columns = ['name', 'email', 'phone_no', 'p_hash',
                    'role', 'actual_role', 'schedule', 'services', 'confirmed']
    column_searchable_list = (
        'name', 'email', 'phone_no')


class DoctorView(ModelView):
    column_hide_backrefs = False

    form_columns = ['name', 'email', 'phone_no', 'p_hash',
                    'role', 'actual_role', 'confirmed', 'specialty', 'price', 'schedule']
    column_searchable_list = (
        'name', 'email', 'phone_no')


class AdminView(ModelView):
    form_columns = ['name', 'email', 'phone_no', 'p_hash',
                    'role', 'actual_role', 'confirmed']
    column_searchable_list = (
        'name', 'email')


db.create_all()
# def is_accessible(self):
# return current_user.is_authenticated

# def inaccessible_callback(self, name, **kwargs):
# return(url_for('login'))


# class MyAdminIndexView(AdminIndexView):
# def is_accessible(self):
#  return current_user.is_authenticated
# admin = Admin(app, index_view=MyAdminIndexView())
# endpoint to avoid blueprints collision
admin.add_view(PatientView(Patient, db.session, endpoint='Patient'))
admin.add_view(DoctorView(
    Doctor, db.session, endpoint='Doctor'))
admin.add_view(AdminView(Admin, db.session, endpoint='Admin'))
admin.add_view(MedicalView(Medical_Specialty,
                           db.session, endpoint='MedicalSpecialty'))
admin.add_view(ScheduleView(Doctor_Schedule,
                            db.session, endpoint='Doctor_Shedule'))

admin.add_view(PScheduleView(Patient_Schedule,
                             db.session, endpoint='Patient_Schedule'))
admin.add_view(ServicesView(Services,
                            db.session, endpoint='Services'))
