from flask import Blueprint, jsonify, request
from database import Users, Appointments, db, Treatments



doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/doctor/appointments/<int:doctor_id>')
def doc_appoint(doctor_id):
    appts = Appointments.query.filter_by(d_id=doctor_id).all()
    result = []
    for a in appts:
        patient = Users.query.get(a.p_id)
        result.append({"id": a.id, "patient": patient.name if patient else "Unknown", "patient_id": a.p_id, "date": a.date, "time": a.time, "status": a.status})
    return jsonify(result)

@doctor_bp.route('/doctor/avail', methods=['POST'])
def avail():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    db.session.commit()
    return jsonify({"message": "Availability set"})

@doctor_bp.route('/doctor/complete/<int:appt_id>', methods=['POST'])
def complete(appt_id):
    data = request.get_json()
    appt = Appointments.query.get(appt_id)
    if not appt:
        return jsonify({"message": "Appointment not found"}), 404
    if appt.status != "Booked":
        return jsonify({"message": "Appointment already processed"}), 400
    appt.status = "Completed"
    treatment = Treatments(appoint_id=appt_id, diagnosis=data.get('diagnosis'), prescription=data.get('prescription'), notes=data.get('notes'))
    db.session.add(treatment)
    db.session.commit()
    return jsonify({"message": "Appointment completed"})

@doctor_bp.route('/doctor/cancel/<int:appt_id>', methods=['PUT'])
def cancel(appt_id):
    appt = Appointments.query.get(appt_id)
    if not appt:
        return jsonify({"message": "Appointment not found"}), 404
    if appt.status != "Booked":
        return jsonify({"message": "Appointment already processed"}), 400
    appt.status = "Cancelled"
    db.session.commit()
    return jsonify({"message": "Appointment cancelled"})

@doctor_bp.route('/doctor/phist/<int:patient_id>/<int:doctor_id>', methods=['GET'])
def phist(patient_id, doctor_id):
    appts = Appointments.query.filter_by(p_id=patient_id, d_id=doctor_id, status="Completed").all()
    his = []
    for a in appts:
        treat = Treatments.query.filter_by(appoint_id=a.id).first()
        his.append({"date": a.date, "diagnosis": treat.diagnosis if treat else "", "prescription": treat.prescription if treat else "", "notes": treat.notes if treat else ""})
    return jsonify(his)
