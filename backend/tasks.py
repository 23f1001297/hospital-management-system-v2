from celery_worker import celery
from database import db, Appointments, Users, Doctor
from datetime import date, datetime
import csv
import os
import smtplib
from email.message import EmailMessage
import logging
logging.basicConfig(level=logging.INFO)



def send_mail(to_email, subject, content):
    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = 'rdrn64@gmail.com'
    message['To'] = to_email
    message.set_content(content)
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('rdrn64@gmail.com', 'srigxvazxovwnskq')
        smtp.send_message(message)

@celery.task
def daily_remainder():
    today = str(date.today())
    appts = Appointments.query.filter_by(date=today, status="Booked").all()
    for a in appts:
        patient = Users.query.get(a.p_id)
        doctor = Users.query.get(a.d_id)
        content = f"Hello {patient.name}, you have an appointment with Dr.{doctor.name} at {a.time} today."
        send_mail(patient.username, "Appointment Remainder", content)
        logging.info(f"Remainder sent to {patient.name}, appointment with Dr.{doctor.name} at {a.time}")
    return "Daily remainder task completed"

@celery.task
def monthly_doctor_report():
    today = datetime.today()
    current_month = today.month
    current_year = today.year
    doctors = Users.query.filter_by(role="doctor").all()
    for doc in doctors:
        appoints = Appointments.query.filter_by(d_id=doc.id, status="Completed").all()
        filename = f"doctor_{doc.id}_{current_month}.html"
        with open(filename, "w") as f:
            f.write(f"<h1>Monthly Report for Dr.{doc.name}</h1>")
            f.write(f"<h3> Month: {current_month}/{current_year}</h3>")
            f.write("<table border='1'>")
            f.write("<tr><th>Date</th><th>Patient</th></tr>")

            for a in appoints:
                appt_date = datetime.strptime(a.date, "%Y-%m-%d")
                if appt_date.month == current_month and appt_date.year == current_year:
                    patient = Users.query.get(a.p_id)
                    f.write(f"<tr><td>{a.date}</td><td>{patient.name}</td></tr>")
            f.write("</table>")
        print(f"Monthly report generated for Dr.{doc.name}")
    return "Monthly report created"

@celery.task
def export_patient_data(patient_id):
    appts = Appointments.query.filter_by(p_id=patient_id, status="Completed").all()
    filename = f"patient_{patient_id}.csv"

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Doctor", "Diagnosis", "Treatment"])
        for a in appts:
            doctor = Users.query.get(a.d_id)
            writer.writerow([a.date, doctor.name if doctor else "", a.diagnosis, a.treatment])
        print(f"CSV generated for patient{patient_id}")
    return filename

def get_daily():
    today = str(date.today())
    appts = Appointments.query.filter(Appointments.date == str(date.today()), Appointments.status.in_(["Booked", "Completed"])).all()
    tasks = []
    for a in appts:
        patient = Users.query.get(a.p_id)
        doctor = Users.query.get(a.d_id)
        tasks.append({"patient": patient.name, "doctor": doctor.name, "time": a.time})
    return{"date": today, "task": tasks if tasks else "No appointment today"}

def get_monthly():
    today = datetime.today()
    current_month = today.month
    current_year = today.year
    doctors = Users.query.filter_by(role="doctor").all()
    report = []
    for doc in doctors:
        appoints = Appointments.query.filter_by(d_id=doc.id, status="Completed").all()
        total = len([a for a in appoints if int(a.date.split("-")[1]) == current_month])
        report.append({"doctor": doc.name, "completed_appointments": total})
    return {"month": today.strftime("%B""%Y"), "report": report}
