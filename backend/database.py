from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    name = db.Column(db.String())
    role  = db.Column(db.String(), nullable=False)
    blacklist = db.Column(db.Boolean, default=False)
    mobile = db.Column(db.String())
    age = db.Column(db.Integer)
    gender = db.Column(db.String())
    address = db.Column(db.Text)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    special = db.Column(db.String())
    availability = db.Column(db.String())

class Appointments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    p_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    d_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.String())
    time = db.Column(db.String())
    status = db.Column(db.String(), default = 'Booked')
    remarks = db.Column(db.Text)

class Treatments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appoint_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
