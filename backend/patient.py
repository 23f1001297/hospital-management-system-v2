from flask import Blueprint, request, jsonify
from database import db, Users, Appointments, Treatments, Doctor

patient_bp = Blueprint('patient_bp', __name__)

@patient_bp.route('/patient/docs', methods=['GET'])
def docs():
    doctor = db.session.query(Users, Doctor)\
        .join(Doctor, Doctor.user_id == Users.id)\
        .filter(Users.role == 'doctor')\
        .all()
    data = []
    for user, doc in doctor:
        data.append({"id": user.id, "name": user.name, "special": doc.special, "availability": doc.availability})
    return jsonify(data)
    

@patient_bp.route('/patient/book', methods=['POST'])
def book():
    data = request.json
    exist = Appointments.query.filter_by(d_id=data['doctor_id'], date=data['date'], time=data['time'], status="Booked").first()
    if exist:
        return  jsonify({"message": "Slot already booked"}), 400
    new_a = Appointments(p_id=data['patient_id'], d_id=data['doctor_id'], date=data['date'], time=data['time'], status="Booked")
    db.session.add(new_a)
    db.session.commit()
    return jsonify({"message": "Appointment booked"})

@patient_bp.route('/patient/appo/<int:patient_id>', methods=['GET'])
def appo(patient_id):
    appts = Appointments.query.filter_by(p_id=patient_id).all()
    result = []
    for a in appts:
        user = Users.query.get(a.d_id)
        result.append({"id": a.id, "doctor": user.name if user else "", "date": a.date, "time": a.time, "status": a.status})
    return jsonify(result)

@patient_bp.route('/patient/cancels/<int:appt_id>', methods=['PUT'])
def cancels(appt_id):
    appt = Appointments.query.get(appt_id)
    if appt:
        appt.status = "Cancelled"
        db.session.commit()
        return jsonify({"message": "Cancelled"})
    return jsonify({"error": "Not found"}), 404

@patient_bp.route('/patient/history/<int:patient_id>', methods=['GET'])
def history(patient_id):
    appts = Appointments.query.filter_by(p_id=patient_id, status="Completed").all()
    result = []
    for a in appts:
        treat = Treatments.query.filter_by(appoint_id=a.id).first()
        doc = Users.query.get(a.d_id)
        result.append({"date": a.date, "doctor": doc.name if doc else "", "diagnosis": treat.diagnosis if treat else "", "prescription": treat.prescription if treat else "", "notes": treat.notes if treat else ""})
    return  jsonify(result)
    

@patient_bp.route('/patient/export/<int:patient_id>', methods=['GET'])
def export(patient_id):
    from tasks import export_patient_data
    export_patient_data.delay(patient_id)
    return jsonify({"message": "Export started successfully"})
